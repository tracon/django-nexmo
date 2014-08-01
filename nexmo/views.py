import logging

from django.http import HttpResponse

from .error_messages import (NEXMO_STATUSES, UNKNOWN_STATUS,
                             NEXMO_MESSAGES, UNKNOWN_MESSAGE)

from .models import InboxTmp

logger = logging.getLogger(__name__)

def nexmo_delivery(request):
    """Callback URL for Nexmo."""
    message_id = request.GET.get('messageId')
    status_id = request.GET.get('status')
    status_msg = NEXMO_STATUSES.get(status_id, UNKNOWN_STATUS)
    error_id = int(request.GET.get('err-code'))
    error_msg = NEXMO_MESSAGES.get(error_id, UNKNOWN_MESSAGE)

    

    # Nexmo expects a 200 response code
    return HttpResponse('')

def nexmo_message(request):
    """Callback URL for Nexmo."""
    messageId = request.GET.get('messageId')
    message_text = request.GET.get('text')
    concat_ref = request.GET.get('concat-ref')
    concat_part = request.GET.get('concat-part')
    concat_total = request.GET.get('concat-total')
    timestamp = request.GET.get('message-timestamp')

    message = InboxTmp(messageId=messageId, message=message_text, concat_ref=concat_ref, concat_part=concat_part, concat_total=concat_total, nexmo_timestamp=timestamp)
    message.save()

    # Nexmo expects a 200 response code
    return HttpResponse('')
