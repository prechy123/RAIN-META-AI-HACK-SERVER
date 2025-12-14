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
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #fafafa; font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #fafafa; padding: 40px 20px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
          <tr>
            <td style="padding: 32px 40px 24px; background: #155dfc; display: flex; align-items: center; justify-content: space-between;">
              <div>
                <h1 style="margin: 0; color: #ffffff; font-size: 22px; font-weight: 600; letter-spacing: -0.3px;">
                  New Support Request
                </h1>
                <p style="margin: 8px 0 0; color: rgba(255,255,255,0.9); font-size: 14px; font-weight: 400;">
                  A customer needs your attention
                </p>
              </div>
              <img src="https://rain-meta-hack-web.vercel.app/logo.jpeg" alt="SharpChat Logo" width="100" style="display: block; border-radius: 24px;">
            </td>
          </tr>
          <tr>
            <td style="padding: 32px 40px 0;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="padding: 12px 0; border-bottom: 1px solid #f5f5f7;">
                    <span style="color: #86868b; font-size: 13px; font-weight: 500;  letter-spacing: 0.5px;">Customer Email</span>
                    <p style="margin: 4px 0 0; color: #1d1d1f; font-size: 15px; font-weight: 400;">
                      <a href="mailto:{user_email}" style="color: #0071e3; text-decoration: none;">{user_email}</a>
                    </p>
                  </td>
                </tr>
                <tr>
                  <td style="padding: 12px 0;">
                    <span style="color: #86868b; font-size: 13px; font-weight: 500;  letter-spacing: 0.5px;">Customer Phone</span>
                    <p style="margin: 4px 0 0; color: #1d1d1f; font-size: 15px; font-weight: 400;">
                      <a href="tel:{user_phone}" style="color: #0071e3; text-decoration: none;">{user_phone}</a>
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td style="padding: 32px 40px 0;">
              <h2 style="margin: 0 0 12px; color: #1d1d1f; font-size: 17px; font-weight: 600; letter-spacing: -0.2px;">
                Request
              </h2>
              <div style="background-color: #155dfc1a; padding: 16px 20px; border-radius: 6px;">
                <p style="margin: 0; color: #1d1d1f; font-size: 15px; line-height: 1.5;">
                  {support_request}
                </p>
              </div>
            </td>
          </tr>
          <tr>
            <td style="padding: 32px 40px;">
              <h2 style="margin: 0 0 12px; color: #1d1d1f; font-size: 17px; font-weight: 600; letter-spacing: -0.2px;">
                Conversation History
              </h2>
              <div style="background-color: #155dfc1a; padding: 20px; border-radius: 8px; font-size: 14px; line-height: 1.6; color: #1d1d1f; white-space: pre-wrap;">
                {conversation_summary}
              </div>
            </td>
          </tr>
          <tr>
            <td style="padding: 0 40px 32px;">
              <div style="border-top: 1px solid #f5f5f7; padding-top: 24px;">
                <p style="margin: 0; color: #86868b; font-size: 13px; line-height: 1.5;">
                  Sent via SharpChat AI, <a href="https://rain-meta-hack-web.vercel.app/" target="_blank" style="color: #0071e3; text-decoration: none;">CLICK TO REGISTER YOUR BUSINESS WITH US.</a>
                </p>
                <p style="margin: 8px 0 0; color: #86868b; font-size: 13px; line-height: 1.5;">
                  Reply to <a href="mailto:{user_email}" style="color: #0071e3; text-decoration: none;">{user_email}</a> or call <a href="tel:{user_phone}" style="color: #0071e3; text-decoration: none;">{user_phone}</a>
                </p>
              </div>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
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
