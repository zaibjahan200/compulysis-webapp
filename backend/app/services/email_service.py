from email.message import EmailMessage
import smtplib
import socket
import ssl
import urllib.request
import json
from typing import Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

def resolve_hostname_via_doh(hostname: str) -> str:
    """Resolve hostname to IPv4 via Google DNS-over-HTTPS to bypass AWS Lambda DNS bugs."""
    try:
        url = f"https://dns.google/resolve?name={hostname}&type=A"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            for answer in data.get('Answer', []):
                if answer['type'] == 1:  # A record
                    return answer['data']
    except Exception as e:
        logger.warning(f"DoH resolution failed for {hostname}: {e}")
    return socket.gethostbyname(hostname)  # Fallback

class PatchedSMTP(smtplib.SMTP):
    """Custom SMTP that uses DoH for DNS resolution to bypass EBUSY errors."""
    def _get_socket(self, host, port, timeout):
        ip = resolve_hostname_via_doh(host)
        logger.info(f"Resolved {host} to {ip} via DoH")
        return socket.create_connection((ip, port), timeout, self.source_address)

class PatchedSMTP_SSL(smtplib.SMTP_SSL):
    """Custom SMTP_SSL that uses DoH for DNS resolution to bypass EBUSY errors."""
    def _get_socket(self, host, port, timeout):
        ip = resolve_hostname_via_doh(host)
        logger.info(f"Resolved {host} to {ip} via DoH")
        return socket.create_connection((ip, port), timeout, self.source_address)

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

        try:
            # Try standard SMTP (Port 587) first
            logger.info(f"Attempting SMTP connection to {host}:587 via PatchedSMTP")
            with PatchedSMTP(host, 587, timeout=15) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(user, password)
                server.send_message(message)
                logger.info("Email sent successfully via port 587.")
                return

        except Exception as exc1:
            logger.warning(f"SMTP on port 587 failed: {str(exc1)}. Trying SMTP_SSL on port 465...")
            try:
                # Fallback to SMTP_SSL (Port 465) if 587 fails (e.g., due to Vercel port blocking)
                with PatchedSMTP_SSL(host, 465, timeout=15) as server:
                    server.login(user, password)
                    server.send_message(message)
                    logger.info("Email sent successfully via SSL port 465.")
                    return
            except Exception as exc2:
                error_msg = f"Failed to send email. Port 587 error: {exc1}. Port 465 error: {exc2}."
                logger.error(error_msg)
                raise RuntimeError(error_msg) from exc2
