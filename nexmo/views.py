from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import InboundMessage, DeliveryStatusFragment, OutboundMessage
from .forms import DeliveryForm, MessageForm


@require_POST
@csrf_exempt
def nexmo_delivery(request, key):
    if key != settings.NEXMO_INBOUND_KEY:
        return HttpResponseForbidden()

    form = DeliveryForm(request.POST)

    if not form.is_valid():
        return HttpResponseBadRequest

    ref_id = form.cleaned_data.get('client-ref')

    if ref_id != 0:
        message = OutboundMessage.objects.get(pk=ref_id)
        status = DeliveryStatusFragment(
            message=message,
            nexmo_message_id=form.cleaned_data['messageId'],
            error_code=form.cleaned_data['err-code'],
            status_msg=form.cleaned_data['status'],
            status_timestamp=form.cleaned_data['message-timestamp'],
        )
        status.save()
        DeliveryStatusFragment.handle_message_status(message)

    # Nexmo expects a 200 response code
    return HttpResponse('')


@require_POST
@csrf_exempt
def nexmo_message(request, key):
    if key != settings.NEXMO_INBOUND_KEY:
        return HttpResponseForbidden()

    form = MessageForm(request.POST)

    if not form.is_valid():
        return HttpResponseBadRequest

    InboundMessage.new_message(
        nexmo_message_id=form.cleaned_data['messageId'],
        message=form.cleaned_data['text'],
        sender=form.cleaned_data['msisdn'],
        concat_ref=form.cleaned_data['concat-ref'],
        concat_part=form.cleaned_data['concat-part'],
        concat_total=form.cleaned_data['concat-total'],
        nexmo_timestamp=form.cleaned_data['message-timestamp'],
    )

    # Nexmo expects a 200 response code
    return HttpResponse('')
