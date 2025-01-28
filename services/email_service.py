import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class EmailServices:
    def __init__(self):
        self.smtp_host = os.environ.get('SMTP_HOST')