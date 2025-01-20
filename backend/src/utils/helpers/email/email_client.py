from email.mime.text import MIMEText
from jinja2 import Template, Environment, FileSystemLoader
import smtplib

from src.config.config import settings
from src.database.graph.crud.bookclubs import BookClubCRUDRepositoryGraph
from src.utils.helpers.email.templates.style_variables import styles
from src.utils.logging.logger import logger

class EmailClient:
    def __init__(self):
        self.mail_server =  settings.MAIL_SERVER 
        self.mail_port = settings.MAIL_PORT 
        self.mail_username = settings.MAIL_USERNAME
        self.mail_password = settings.MAIL_PASSWORD
        self.mail_from = settings.MAIL_FROM
        self.mail_from_name = settings.MAIL_FROM_NAME
        self.template_loader = FileSystemLoader('./src/utils/helpers/email/templates/')

    def send_invite_email(
            self, 
            to_email:str,
            invite_id:str,
            book_club_id:str,
            invite_user_username:str,
            subject:str,
            book_club_repo:BookClubCRUDRepositoryGraph,
            is_debug: bool = False):

        response = book_club_repo.get_book_club_name_and_current_book(
            book_club_id
        )
        
        with open("./src/utils/helpers/email/templates/invite.html", "r") as file:
            template_str = file.read()
        
        jinja_template = Environment(loader=self.template_loader).from_string(template_str)
        book_club_name = response['book_club_name']
        # jinja_template = Template(template_str)
        
        if response['book_club_name'] is None:
            raise ValueError("Book club not found")

        email_context = {
            'invite_user_username': invite_user_username,
            'book_club_name': book_club_name,
            'invite_id': invite_id,
            'styles': styles,
        }

        if response['current_book'] is None:
            email_context['current_book'] = False
            email_content = jinja_template.render(email_context)

        else:
            email_context['current_book'] = True
            email_context['current_book_title'] = response['current_book'].title
            email_context['current_book_img'] = response['current_book'].small_img_url
            email_context['current_book_authors'] = ", ".join(response['current_book'].author_names)

            email_content = jinja_template.render(email_context)

        # print(email_content)
        
        msg = MIMEText(email_content, 'html')
        msg['Subject'] = subject
        msg['From'] = f"{self.mail_from_name} <{self.mail_from}>"
        msg['To'] = to_email
        
        if not is_debug:
            with smtplib.SMTP_SSL(self.mail_server, self.mail_port) as smtp_server:
                smtp_server.login(self.mail_from, self.mail_password)
                smtp_server.sendmail(self.mail_from, to_email, msg.as_string())
                logger.info(
                    "Invite Email Sent",
                    extra={
                        "to_email": to_email,
                        "invite_id": invite_id,
                        "book_club_id": book_club_id,
                        "invite_user_username": invite_user_username,
                        "action": "send_invite_email"
                    }
                )
        else: 
            return email_content

email_client = EmailClient()
