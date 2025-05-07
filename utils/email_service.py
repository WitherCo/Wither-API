import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

logger = logging.getLogger(__name__)

def send_email(to, subject, body, html=None, cc=None, bcc=None, reply_to=None):
    """
    Send an email using the configured SMTP server
    
    Args:
        to: Recipient email address or list of addresses
        subject: Email subject
        body: Plain text email body
        html: HTML email body (optional)
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
        reply_to: Reply-To email address (optional)
        
    Returns:
        dict: Status of the operation
    """
    try:
        # Get email configuration
        smtp_server = current_app.config.get('MAIL_SERVER')
        smtp_port = current_app.config.get('MAIL_PORT')
        use_tls = current_app.config.get('MAIL_USE_TLS')
        username = current_app.config.get('MAIL_USERNAME')
        password = current_app.config.get('MAIL_PASSWORD')
        sender = current_app.config.get('MAIL_DEFAULT_SENDER')
        
        # Validate configuration
        if not all([smtp_server, smtp_port, sender]):
            logger.error("Email configuration is incomplete")
            return {
                'status': 'error',
                'error': 'Email service is not properly configured'
            }
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender
        
        # Convert to list if to is a string
        to_list = to if isinstance(to, list) else [to]
        msg['To'] = ', '.join(to_list)
        
        # Add CC if provided
        if cc:
            cc_list = cc if isinstance(cc, list) else [cc]
            msg['Cc'] = ', '.join(cc_list)
            to_list.extend(cc_list)
        
        # Add BCC if provided
        if bcc:
            bcc_list = bcc if isinstance(bcc, list) else [bcc]
            to_list.extend(bcc_list)
        
        # Add Reply-To if provided
        if reply_to:
            msg['Reply-To'] = reply_to
        
        # Add plain text body
        msg.attach(MIMEText(body, 'plain'))
        
        # Add HTML body if provided
        if html:
            msg.attach(MIMEText(html, 'html'))
        
        # Connect to SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        
        if use_tls:
            server.starttls()
        
        # Login if credentials are provided
        if username and password:
            server.login(username, password)
        
        # Send email
        server.sendmail(sender, to_list, msg.as_string())
        server.quit()
        
        logger.info(f"Email sent to {to}")
        
        return {
            'status': 'success'
        }
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }
