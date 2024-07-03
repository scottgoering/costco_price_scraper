import smtplib
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from costco_price_scraper.utils import config


def send_email(subject, body, to_email, attachment_paths=None):
    # Email configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 465
    sender_email, sender_password = config.read_sender_email_config()

    # Create MIME object
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject

    # Attach body text
    msg.attach(MIMEText(body, "html"))

    # Attach image
    if attachment_paths:
        for attachment_path in attachment_paths:
            filename = os.path.basename(attachment_path)
            with open(attachment_path, "rb") as attachment:
                image = MIMEImage(attachment.read())
                image.add_header(
                    "Content-Disposition", f'attachment; filename="{filename}"'
                )
                msg.attach(image)

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())


