from datetime import datetime

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.timezone import utc
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import InboundMessageFragment, DeliveryStatusFragment, OutboundMessage


@require_POST
@csrf_exempt
def nexmo_delivery(request, key):
    if key != settings.NEXMO_INBOUND_KEY:
        return HttpResponseForbidden()

    form = DeliveryForm(request.POST)

    if not form.is_valid():
        return HttpResponse('', status=400)

    ref_id = form.cleaned_data.get('client-ref')

    if ref_id != 0:
        message = OutboundMessage.objects.get(pk=ref_id)
        status = DeliveryStatusFragment(
            message=message,
            messageId=form.cleaned_data['messageId'],
            error_code=form.cleaned_data['err-code'],
            status_msg=form.cleaned_data['status'],
            status_timestamp=form.cleaned_data['message-timestamp'],
        )
        status.save()

    # Nexmo expects a 200 response code
    return HttpResponse('')


@require_POST
@csrf_exempt
def nexmo_message(request, key):
    if key != settings.NEXMO_INBOUND_KEY:
        return HttpResponseForbidden()
    messageId = request.POST.get('messageId')
    message_text = request.POST.get('text')
    sender = request.POST.get('msisdn')
    concat_ref = request.POST.get('concat-ref')
    concat_part = int(request.POST.get('concat-part') or 0 )
    concat_total = int(request.POST.get('concat-total') or 0 )
    timestamp = request.POST.get('message-timestamp')

    GMTtimestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').replace(tzinfo=utc)

    # Magic happens in the InboundMessageFragment. If the message was single-part, it will be saved directly to the InboundMessage. Multi-part messages will be saved to InboundMessage when all the parts are received.
    message = InboundMessageFragment(messageId=messageId, message=message_text, sender=sender, concat_ref=concat_ref, concat_part=concat_part, concat_total=concat_total, nexmo_timestamp=GMTtimestamp)
    message.save()

    # Nexmo expects a 200 response code
    return HttpResponse('')
