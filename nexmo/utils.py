import logging
from .libpynexmo.nexmomessage import NexmoMessage
from django.conf import settings

logger = logging.getLogger(__name__)

outbox = []

def send_message(to, message, api_key=settings.NEXMO_USERNAME, api_secret=settings.NEXMO_PASSWORD):
    """Shortcut to send a sms using libnexmo api.

    Usage:

    >>> from nexmo import send_message
    >>> send_message('+33612345678', 'My sms message body')
    """
    params = {
        'api_key': api_key,
        'api_secret': api_secret,
        'from': settings.NEXMO_FROM,
        'to': to,
        'status-report-req': 0,
        'text': message.encode('utf-8'),
    }

    sms = NexmoMessage(params)

    response = sms.send_request()
    return response

def get_balance():
    """Shortcut to check balance.

    Usage:

    >>> from nexmo import get_balance
    >>> get_balance()
    """

    params = {
        'api_key': settings.NEXMO_USERNAME,
        'api_secret': settings.NEXMO_PASSWORD,
        'type': 'balance'
    }

    sms = NexmoMessage(params)
    response = sms.send_request()
    return response['value']
