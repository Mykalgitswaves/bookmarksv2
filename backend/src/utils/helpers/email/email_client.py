from email.mime.text import MIMEText
import smtplib

from src.config.config import settings
from src.database.graph.crud.bookclubs import BookClubCRUDRepositoryGraph

class EmailClient:
    def __init__(self):
        self.mail_server =  settings.MAIL_SERVER 
        self.mail_port = settings.MAIL_PORT 
        self.mail_username = settings.MAIL_USERNAME
        self.mail_password = settings.MAIL_PASSWORD
        self.mail_from = settings.MAIL_FROM
        self.mail_from_name = settings.MAIL_FROM_NAME

    def send_invite_email(
            self, 
            to_email:str,
            invite_id:str,
            book_club_id:str,
            invite_user_username:str,
            subject:str,
            book_club_repo:BookClubCRUDRepositoryGraph):

        response = book_club_repo.get_book_club_name_and_current_book(
            book_club_id)
        
        book_club_name = response['book_club_name']

        if response['book_club_name'] is None:
            raise ValueError("Book club not found")

        if response['current_book'] is None:
            invite_body = f"""
            <html>
                <body>
                    <p>Hi,</p>
                    <p>{invite_user_username} have been invited to join {book_club_name}.</p>
                    <p>Please click the link below to register.</p>
                    <a href="hardcoverlit.com/{invite_id}">Click here to register</a>
                    <p>Thanks</p>
                </body>
            </html>
            """
        else:
            current_book_title = response['current_book'].title
            current_book_img = response['current_book'].small_img_url
            current_book_authors = ", ".join(response['current_book'].author_names)
            
            invite_body = f"""
            <html>
                <body>
                    <p>Hi,</p>
                    <p>{invite_user_username} have been invited to join {book_club_name}.</p>
                    <p>They are reading {current_book_title} by {current_book_authors}.</p>
                    <p>Please click the link below to register.</p>
                    <a href="hardcoverlit.com/{invite_id}">Click here to register</a>
                    <p>Thanks</p>
                </body>
            </html>
            """

        print(invite_body)
        
        msg = MIMEText(invite_body, 'html')
        msg['Subject'] = subject
        msg['From'] = f"{self.mail_from_name} <{self.mail_from}>"
        msg['To'] = to_email

        with smtplib.SMTP_SSL(self.mail_server, self.mail_port) as smtp_server:
            smtp_server.login(self.mail_from, self.mail_password)
            smtp_server.sendmail(self.mail_from, to_email, msg.as_string())
            print("Message sent!")

email_client = EmailClient()