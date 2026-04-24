from email.message import EmailMessage
import smtplib
import socket
from typing import Optional

from app.core.config import settings

# --- VERCEL PYTHON 3.12 BUGFIX ---
# Vercel's AWS Lambda Python 3.12 runtime has a bug where dual-stack (IPv4+IPv6) 
# DNS resolution throws "OSError: [Errno 16] Device or resource busy".
# We monkey-patch socket.getaddrinfo to force IPv4 (AF_INET), which bypasses it.
_orig_getaddrinfo = socket.getaddrinfo

def _ipv4_only_getaddrinfo(*args, **kwargs):
    args_list = list(args)
    if len(args_list) >= 3 and args_list[2] == 0:
        args_list[2] = socket.AF_INET
    elif 'family' in kwargs and kwargs['family'] == 0:
        kwargs['family'] = socket.AF_INET
    return _orig_getaddrinfo(*args_list, **kwargs)

socket.getaddrinfo = _ipv4_only_getaddrinfo
# ---------------------------------


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

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30) as server:
                server.ehlo()
                if settings.SMTP_TLS:
                    server.starttls()
                    server.ehlo()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(message)
        except smtplib.SMTPException as exc:
            raise RuntimeError(f"Failed to send email: {str(exc)}") from exc
