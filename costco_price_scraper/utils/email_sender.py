import smtplib
import configparser
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders


def read_email_config():
    """Reads sender email config from the configuration file."""
    config = configparser.ConfigParser()
    config.read("config.ini")
    return (
        config["Credentials"]["GMAIL_USERNAME"],
        config["Credentials"]["GMAIL_PASSWORD"],
    )


def send_email(subject, body, to_email, attachment_paths=None):
    # Email configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 465
    sender_email, sender_password = read_email_config()

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

    # Attach any other file
    # if attachment_path:
    #     attachment = open(attachment_path, 'rb')
    #     base = MIMEBase('application', 'octet-stream')
    #     base.set_payload(attachment.read())
    #     encoders.encode_base64(base)
    #     base.add_header('Content-Disposition', f'attachment; filename={attachment_path}')
    #     msg.attach(base)
    #     attachment.close()

    # Establish a connection with the SMTP server
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        # server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())


# Example usage
