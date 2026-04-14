import smtplib
from email.message import EmailMessage

import httpx

from app.core.config import get_settings


class EmailService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str) -> dict:
        provider = self.settings.email_provider.lower()
        if provider == "resend":
            return self._send_with_resend(to_email, subject, html_content, text_content)
        if provider == "sendgrid":
            return self._send_with_sendgrid(to_email, subject, html_content, text_content)
        return self._send_with_smtp(to_email, subject, html_content, text_content)

    def _send_with_resend(self, to_email: str, subject: str, html_content: str, text_content: str) -> dict:
        response = httpx.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {self.settings.email_provider_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": self.settings.email_from,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
                "text": text_content,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        return {"provider": "resend", "success": True, "response": response.json()}

    def _send_with_sendgrid(self, to_email: str, subject: str, html_content: str, text_content: str) -> dict:
        response = httpx.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {self.settings.email_provider_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "personalizations": [{"to": [{"email": to_email}]}],
                "from": {"email": self.settings.email_from},
                "subject": subject,
                "content": [
                    {"type": "text/plain", "value": text_content},
                    {"type": "text/html", "value": html_content},
                ],
            },
            timeout=30.0,
        )
        response.raise_for_status()
        return {"provider": "sendgrid", "success": True, "status_code": response.status_code}

    def _send_with_smtp(self, to_email: str, subject: str, html_content: str, text_content: str) -> dict:
        if not self.settings.smtp_host:
            raise ValueError("SMTP_HOST is required when EMAIL_PROVIDER=smtp")

        message = EmailMessage()
        message["From"] = self.settings.email_from
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(text_content)
        message.add_alternative(html_content, subtype="html")

        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port) as server:
            if self.settings.smtp_use_tls:
                server.starttls()
            if self.settings.smtp_username and self.settings.smtp_password:
                server.login(self.settings.smtp_username, self.settings.smtp_password)
            server.send_message(message)

        return {"provider": "smtp", "success": True}
