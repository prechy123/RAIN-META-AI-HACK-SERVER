"""
Email service for sending support requests to business owners
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.conf import settings

logger = logging.getLogger("email_service")


async def send_support_email(
    business_name: str,
    business_email: str,
    user_email: str,
    user_phone: str,
    conversation_summary: str,
    support_request: str
) -> bool:
    """
    Send email to business owner about customer support request.
    
    Args:
        business_name: Name of the business
        business_email: Business owner's email
        user_email: Customer's email
        user_phone: Customer's phone number
        conversation_summary: Summary of the conversation
        support_request: What the customer needs
        
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        # Create email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"SharpChat AI - Customer Support Request for {business_name}"
        msg['From'] = settings.EMAIL_FROM
        msg['To'] = business_email
        
        # Email body (HTML)
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
              <h2 style="color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px;">
                📧 New Customer Support Request
              </h2>
              
              <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #1f2937;">Customer Information:</h3>
                <p><strong>Email:</strong> {user_email}</p>
                <p><strong>Phone:</strong> {user_phone}</p>
              </div>
              
              <div style="margin: 20px 0;">
                <h3 style="color: #1f2937;">Support Request:</h3>
                <p style="background-color: #fef3c7; padding: 15px; border-left: 4px solid #f59e0b; border-radius: 4px;">
                  {support_request}
                </p>
              </div>
              
              <div style="margin: 20px 0;">
                <h3 style="color: #1f2937;">Conversation Summary:</h3>
                <div style="background-color: #f9fafb; padding: 15px; border-radius: 4px; white-space: pre-wrap;">
{conversation_summary}
                </div>
              </div>
              
              <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
              
              <p style="color: #6b7280; font-size: 14px;">
                This email was sent via <strong>SharpChat AI</strong> - Your intelligent business assistant platform.
                <br>
                Please respond directly to the customer at <a href="mailto:{user_email}">{user_email}</a> or call them at {user_phone}.
              </p>
            </div>
          </body>
        </html>
        """
        
        # Attach HTML body
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        logger.info(f"Sending support email to {business_email}")
        
        with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT_SSL) as server:
            server.login(settings.EMAIL_FROM, settings.EMAIL_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"SUCCESS: Email sent to {business_email}")
        return True
        
    except Exception as e:
        logger.error(f"ERROR: Failed to send email: {str(e)}")
        return False
