import logging
from .libpynexmo.nexmomessage import NexmoMessage
from django.conf import settings

logger = logging.getLogger(__name__)

outbox = []

def send_message(to, message):
    """Shortcut to send a sms using libnexmo api.

    Usage:

    >>> from nexmo import send_message
    >>> send_message('+33612345678', 'My sms message body')
    """
    params = {
        'api_key': settings.NEXMO_USERNAME,
        'api_secret': settings.NEXMO_PASSWORD,
        'type': 'unicode',
        'from': settings.NEXMO_FROM,
        'to': to,
        'text': message.encode('utf-8'),
    }

    sms = NexmoMessage(params)

    #if settings.NEXMO_LOG:
    #    logger.info(u'Nexmo outbound SMS to: %s, message: %s' % (
    #        sms.sms['to'],
    #        sms.sms['text'],
    #    ))

    if settings.NEXMO_TEST_MODE:
        outbox.append(sms)
    else:
        response = sms.send_request()
        return response

    return False
