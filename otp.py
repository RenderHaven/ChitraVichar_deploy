import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Replace with your SMTP config
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "chitravichar.in@gmail.com"
SMTP_PASSWORD = "evez hupc pmmu rpim"

class Email:
    @staticmethod
    def send_email(email_list, subject, body):
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = ''  # You can leave it blank or use a placeholder
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            # Use email_list only as BCC
            server.sendmail(SMTP_USER, email_list, msg.as_string())
            server.quit()
        except Exception as e:
            print(e)
            raise Exception(f"SMTP error: {str(e)}")

