import os
from twilio.rest import Client

def send_whatsapp(to_number, message_body):
# def send_whatsapp(to_number, message_body, content_sid=None):
    # Load Twilio credentials from environment variables
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_number = os.getenv('TWILIO_FROM_NUMBER')

    if not all([account_sid, auth_token, from_number]):
        raise ValueError("Twilio credentials are not properly set in environment variables.")

    # Initialize Twilio client
    client = Client(account_sid, auth_token)

    # Send WhatsApp message
    message = client.messages.create(
        body=message_body,
        # content_sid=content_sid,
        from_=f'whatsapp:{from_number}',
        to=f'whatsapp:{to_number}'
    )

    return message.sid