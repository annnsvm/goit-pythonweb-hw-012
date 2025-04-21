"""
Email Service Module
"""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from aiosmtplib import send

from src.conf.config import settings


async def send_email(email: str, email_content: str):
    """
    Sends a confirmation email to the user.

    Args:
        email (str): The recipient's email address.
        email_content (str): The email's content
    """
    message = MIMEMultipart()
    message["From"] = settings.MAIL_FROM
    message["To"] = email
    message["Subject"] = "Confirm email"

    html_message = MIMEText(email_content, "html")
    message.attach(html_message)

    try:
        await send(
            message,
            hostname=settings.MAIL_SERVER,
            port=settings.MAIL_PORT,
            use_tls=settings.MAIL_SSL_TLS,
            username=settings.MAIL_USERNAME,
            password=settings.MAIL_PASSWORD,
            timeout=10.0,
        )
    except ConnectionError as err:
        print(str(err))