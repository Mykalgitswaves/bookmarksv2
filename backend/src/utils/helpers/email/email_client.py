from email.mime.text import MIMEText
import smtplib

from src.config.config import settings

class EmailClient:
    def __init__(self):
        self.mail_server = '' #settings.MAIL_SERVER 
        self.mail_port = '' #settings.MAIL_PORT 
        self.mail_username = '' #settings.MAIL_USERNAME
        self.mail_password = '' #settings.MAIL_PASSWORD
        self.mail_from = '' #settings.MAIL_FROM
        self.mail_from_name = '' #settings.MAIL_FROM_NAME

        self.invite_body = """
        <html>
            <body>
                <p>Hi,</p>
                <p>You have been invited to join the Bookstore. Please click the link below to register.</p>
                <a href="hardcoverlit.com">Click here to register</a>
                <p>Thanks</p>
            </body>
        </html>
        """

    def send_invite_email(self, to_email, subject):
        msg = MIMEText(self.invite_body, 'html')
        msg['Subject'] = subject
        msg['From'] = f"{self.mail_from_name} <{self.mail_from}>"
        msg['To'] = to_email

        with smtplib.SMTP_SSL(self.mail_server, self.mail_port) as smtp_server:
            smtp_server.login(self.mail_from, self.mail_password)
            smtp_server.sendmail(self.mail_from, to_email, msg.as_string())
            print("Message sent!")

email_client = EmailClient()