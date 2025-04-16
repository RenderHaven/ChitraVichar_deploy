import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Replace with your SMTP config
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "vikrambalai1002@gmail.com"
SMTP_PASSWORD = "wnna bkyf uqga bock"

class Email:
    @staticmethod
    def send_email(email_list, subject, body, cc_list=None):
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = ', '.join(email_list)
        msg['Subject'] = subject
        if cc_list:
            msg['Cc'] = ', '.join(cc_list)
        
        msg.attach(MIMEText(body, 'plain'))

        recipients = email_list + (cc_list if cc_list else [])

        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, recipients, msg.as_string())
            server.quit()
        except Exception as e:
            raise Exception(f"SMTP error: {str(e)}")

