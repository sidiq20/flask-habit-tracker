import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class EmailService:
    def __init__(self):
        self.smtp_host = os.environ.get('SMTP_HOST')
        self.smtp_port = int(os.environ.get('SMTP_PORT', 465))  # Use SSL port
        self.smtp_user = os.environ.get('SMTP_USER')
        self.smtp_pass = os.environ.get('SMTP_PASS')
        self.from_email = os.environ.get('SMTP_FROM')

    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send an email with the given subject and HTML body."""
        if not all([self.smtp_host, self.smtp_port, self.smtp_user, self.smtp_pass, self.from_email]):
            print("❌ Error: SMTP environment variables are not set")
            return False

        try:
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "html"))

            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)

            print(f"✅ Email sent to {to_email}")
            return True
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False
