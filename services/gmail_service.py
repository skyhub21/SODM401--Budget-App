import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging
import socket

import os
import sys

logger = logging.getLogger(__name__)
MAIL_CONFIG = {
    'MAIL_SERVER': os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
    'MAIL_PORT': int(os.getenv('MAIL_PORT', 587)),
    'MAIL_USERNAME': os.getenv('MAIL_USERNAME'),
    'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD'),
    'MAIL_USE_TLS': os.getenv('MAIL_USE_TLS', 'True').lower() == 'true',
    'MAIL_DEFAULT_SENDER': os.getenv('MAIL_DEFAULT_SENDER'),
}
class GmailService:
    """
    Gmail email service using App Password authentication
    This maintains the exact same interface as your original class
    """
    
    def __init__(self, app=None):
        """
        Initialize with Flask app context
        """
        self.smtp_server = None
        self.smtp_port = None
        self.username = None
        self.password = None
        self.use_tls = None
        self.timeout = None
        self.default_sender = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """
        Initialize with Flask app configuration
        """
        self.smtp_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('MAIL_PORT', 587))
        self.username = os.getenv('MAIL_USERNAME')
        self.password = os.getenv('MAIL_PASSWORD')
        self.use_tls = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
        self.timeout = int(os.getenv('MAIL_TIMEOUT', 30))
        self.default_sender = os.getenv('MAIL_DEFAULT_SENDER')
        
        logger.info(f"GmailService initialized with server: {self.smtp_server}:{self.smtp_port}")

    def send_email(self, to_emails, subject, body_html, body_text=None, from_email=None, attachments=None):
        try:
            # Convert single email to list for consistent handling
            if isinstance(to_emails, str):
                to_emails = [to_emails]
            
            successful_sends = 0
            failed_emails = []
            
            for recipient in to_emails:
                try:
                    # Create message container for each recipient
                    print("Create message container for each recipient")
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = subject
                    msg['From'] = from_email or MAIL_CONFIG['MAIL_DEFAULT_SENDER']
                    msg['To'] = recipient
                    
                    # Add plain text version if provided
                    print("Add plain text version if provided")
                    if body_text:
                        text_part = MIMEText(body_text, 'plain')
                        msg.attach(text_part)
                    
                    # Add HTML version
                    print("Add HTML version")
                    html_part = MIMEText(body_html, 'html')
                    msg.attach(html_part)

                    # Add attachments if any
                    '''if attachments:
                        for attachment in attachments:
                            if isinstance(attachment, tuple) and len(attachment) == 3:
                                filename, content_type, data = attachment
                                part = MIMEBase(*content_type.split('/'))
                                part.set_payload(data)
                                encoders.encode_base64(part)
                                part.add_header(
                                    'Content-Disposition',
                                    f'attachment; filename="{filename}"'
                                )
                                msg.attach(part)
                    elif isinstance(attachment, str):
                        # Assume it's a file path
                        with open(attachment, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename="{attachment.split("/")[-1]}"'
                            )
                            msg.attach(part)'''
                    
                    print("🔄 Connecting to SMTP server...")
                    server = smtplib.SMTP(MAIL_CONFIG['MAIL_SERVER'], MAIL_CONFIG['MAIL_PORT'])
                    server.ehlo()
                    
                    if MAIL_CONFIG['MAIL_USE_TLS']:
                        print("🔄 Starting TLS...")
                        server.starttls()
                        server.ehlo()
                    
                    print("🔄 Logging in...")
                    server.login(MAIL_CONFIG['MAIL_USERNAME'], MAIL_CONFIG['MAIL_PASSWORD'])
                    
                    print("🔄 Sending email...")
                    server.send_message(msg)
                    server.quit()
                    
                    successful_sends += 1
                    logger.info(f"Email sent to {recipient}")
                    
                except Exception as e:
                    failed_emails.append(recipient)
                    logger.error(f"Failed to send to {recipient}: {str(e)}")
            
            
            
            logger.info(f"Email sent successfully to {len(to_emails)} recipients")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication failed. Check your username and App Password: {str(e)}")
            raise Exception("Email authentication failed. Please verify your Gmail App Password.")
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {str(e)}")
            raise Exception(f"SMTP error occurred: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            raise Exception(f"Failed to send email: {str(e)}")
    