import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class EmailService:
    def __init__(self):
        self.smtp_host = os.environ.get('SMTP_HOST')
        self.smtp_port = int(os.environ.get('SMTP_PORT', 587))
        self.smtp_user = os.environ.get('SMTP_USER')
        self.smtp_pass = os.environ.get('SMTP_PASS')
        self.from_email = os.environ.get('SMTP_FROM')

    def send_reminder(self, to_email: str, habit_name: str) -> bool:
        if not all([self.smtp_host, self.smtp_port, self.smtp_user, self.smtp_pass, self.from_email]):
            raise ValueError("SMTP environment variables are not properly set")
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = "Don't forget your daily habit!"

            body = f"""
            <html>
              <body>
                <h2>Time to complete your habit!</h2>
                <p>Hi there,</p>
                <p>This is a friendly reminder to complete your habit: <strong>{habit_name}</strong></p>
                <p>Maintaining consistency is key to building good habits. Take a moment to complete it now!</p>
                <p>Best regards,<br>Your Habit Tracker</p>
              </body>
            </html>
            """

            msg.attach(MIMEText(body, 'html'))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)

            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False