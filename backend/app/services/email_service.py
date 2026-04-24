from email.message import EmailMessage
import smtplib
import socket
import ssl
import struct
from typing import Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# RAW DNS RESOLVER — completely bypasses Python's broken socket.getaddrinfo
# on Vercel/AWS-Lambda Python 3.12 (EBUSY bug).
#
# Strategy:
#   1. Open a raw TCP socket to Google Public DNS at 8.8.8.8:53
#      (no hostname resolution needed — it's a literal IP).
#   2. Send a minimal DNS query for the A record of the target hostname.
#   3. Parse the response and return the first IPv4 address.
# ---------------------------------------------------------------------------

def _raw_dns_resolve(hostname: str) -> str:
    """Resolve *hostname* to an IPv4 address via a raw TCP DNS query to 8.8.8.8."""
    # ---- build query ----
    txn_id = 0xABCD
    flags = 0x0100  # standard query, recursion desired
    header = struct.pack(">HHHHHH", txn_id, flags, 1, 0, 0, 0)

    qname = b""
    for label in hostname.split("."):
        qname += bytes([len(label)]) + label.encode("ascii")
    qname += b"\x00"
    question = qname + struct.pack(">HH", 1, 1)  # Type A, Class IN
    query = header + question

    # ---- send over TCP (length-prefixed) ----
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect(("8.8.8.8", 53))  # IP literal — no getaddrinfo
    sock.sendall(struct.pack(">H", len(query)) + query)

    # ---- read response ----
    raw_len = _recv_exact(sock, 2)
    resp_len = struct.unpack(">H", raw_len)[0]
    response = _recv_exact(sock, resp_len)
    sock.close()

    # ---- parse response ----
    answer_count = struct.unpack(">H", response[6:8])[0]
    # skip header (12 bytes), then skip question section
    pos = 12
    # skip our single question
    while response[pos] != 0:
        pos += response[pos] + 1
    pos += 1 + 4  # null terminator + QTYPE(2) + QCLASS(2)

    for _ in range(answer_count):
        # name field (may be a pointer)
        if response[pos] & 0xC0 == 0xC0:
            pos += 2
        else:
            while response[pos] != 0:
                pos += response[pos] + 1
            pos += 1

        rtype, _, _, rdlength = struct.unpack(">HHIH", response[pos : pos + 10])
        pos += 10

        if rtype == 1 and rdlength == 4:  # A record
            ip = socket.inet_ntoa(response[pos : pos + 4])
            logger.info(f"Resolved {hostname} -> {ip} via raw DNS")
            return ip
        pos += rdlength

    raise RuntimeError(f"No A record found for {hostname}")


def _recv_exact(sock: socket.socket, n: int) -> bytes:
    """Read exactly *n* bytes from *sock*."""
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise RuntimeError("DNS socket closed prematurely")
        buf += chunk
    return buf


# ---------------------------------------------------------------------------
# Patched SMTP classes that use _raw_dns_resolve + raw socket.connect
# so that socket.getaddrinfo / socket.create_connection are never called.
# ---------------------------------------------------------------------------

class _RawSMTP(smtplib.SMTP):
    """SMTP subclass that resolves the host via raw DNS and connects via raw socket."""

    def _get_socket(self, host, port, timeout):
        ip = _raw_dns_resolve(host)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))  # IP literal — no getaddrinfo
        return sock


class _RawSMTP_SSL(smtplib.SMTP_SSL):
    """SMTP_SSL subclass that resolves the host via raw DNS and connects via raw socket."""

    def _get_socket(self, host, port, timeout):
        ip = _raw_dns_resolve(host)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))  # IP literal — no getaddrinfo
        # wrap in TLS, preserving the real hostname for SNI / cert verification
        ctx = self.context if self.context else ssl.create_default_context()
        return ctx.wrap_socket(sock, server_hostname=host)


# ---------------------------------------------------------------------------
# EmailService
# ---------------------------------------------------------------------------

class EmailService:
    @staticmethod
    def is_configured() -> bool:
        return bool(settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD)

    @staticmethod
    def send_assessment_report_email(
        recipient_email: str,
        report_id: str,
        patient_name: str,
        risk_level: str,
        total_score: int,
        clinical_notes: Optional[str] = None,
    ) -> None:
        if not EmailService.is_configured():
            raise RuntimeError(
                "SMTP is not configured. Set SMTP_HOST, SMTP_USER, and SMTP_PASSWORD in backend environment."
            )

        from_email = settings.SMTP_USER

        message = EmailMessage()
        message["Subject"] = f"Compulysis Assessment Report - {report_id}"
        message["From"] = from_email
        message["To"] = recipient_email

        text_body = (
            "Compulysis OCD Assessment Report\n\n"
            f"Report ID: {report_id}\n"
            f"Patient Name: {patient_name}\n"
            f"Risk Level: {risk_level}\n"
            f"Total Score: {total_score}/36\n\n"
            "Clinical Notes:\n"
            f"{clinical_notes or 'No clinical notes available.'}\n\n"
            "Please contact your psychologist for detailed interpretation and follow-up planning."
        )

        html_body = f"""
        <html>
          <body>
            <h2>Compulysis OCD Assessment Report</h2>
            <p><strong>Report ID:</strong> {report_id}</p>
            <p><strong>Patient Name:</strong> {patient_name}</p>
            <p><strong>Risk Level:</strong> {risk_level}</p>
            <p><strong>Total Score:</strong> {total_score}/36</p>
            <h3>Clinical Notes</h3>
            <p>{clinical_notes or 'No clinical notes available.'}</p>
            <p>Please contact your psychologist for detailed interpretation and follow-up planning.</p>
          </body>
        </html>
        """

        message.set_content(text_body)
        message.add_alternative(html_body, subtype="html")

        host = settings.SMTP_HOST
        user = settings.SMTP_USER
        password = settings.SMTP_PASSWORD

        # --- attempt 1: STARTTLS on port 587 ---
        first_error = None
        try:
            logger.info(f"Attempting _RawSMTP connection to {host}:587")
            with _RawSMTP(host, 587, timeout=15) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(user, password)
                server.send_message(message)
                logger.info("Email sent successfully via port 587.")
                return
        except Exception as exc1:
            first_error = exc1
            logger.warning(f"Port 587 failed: {exc1}")

        # --- attempt 2: implicit SSL on port 465 ---
        try:
            logger.info(f"Attempting _RawSMTP_SSL connection to {host}:465")
            with _RawSMTP_SSL(host, 465, timeout=15) as server:
                server.login(user, password)
                server.send_message(message)
                logger.info("Email sent successfully via SSL port 465.")
                return
        except Exception as exc2:
            error_msg = f"Failed to send email. Port 587 error: {first_error}. Port 465 error: {exc2}."
            logger.error(error_msg)
            raise RuntimeError(error_msg) from exc2
