import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class EmailServices:
    def __init__(self):
        self.smtp_host = os.environ.get('SMTP_HOST')
        self.smtp_port = int(os.environ.get('SMTP_PORT', 587))
        self.stmp_user = os.environ.get('SMTP_USER')
        self.smtp_pass = os.environ.get('SMTP_PASS')
        self.from_email = os.environ.get('STMP_FROM')

    def send_remainder(self, to_email: str, habit_name: str) -> bool:
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = "Don't forget your daily habit!"

            body = f"""
            <html>
              <body>
                <h2> Time to complete your habit! </h2>
                <p> Hi there, </p>
                <p>This is a friendly reminder to complete you daily streaks: <strong>{habit_name}</strong></p>
                <p>Maintaining consistency is key to building good habits. Take a moment to complete it now!</p>
                <p> Best regards, <br>Your Streaker </br>
                </body>
                </html>
            """

            msg.attach(MIMEText(body, 'html'))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()