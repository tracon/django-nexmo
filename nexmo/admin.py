# encoding: utf-8

from django.contrib import admin

from .models import (
    InboundMessage,
    OutboundMessage
)
from .error_messages import (NEXMO_SEND_STATUS, UNKNOWN_STATUS,
                             NEXMO_MESSAGES, UNKNOWN_MESSAGE)

def send_status_explained(obj):
    return NEXMO_SEND_STATUS.get(obj.send_status, UNKNOWN_STATUS)
send_status_explained.short_description = "Lähetysstatus"

def status_explained(obj):
    return NEXMO_MESSAGES.get(obj.status, UNKNOWN_MESSAGE)
status_explained.short_description = "Välitysstatus"

class InboxAdmin(admin.ModelAdmin):
    model = InboundMessage
    list_display = ['messageId', 'nexmo_timestamp', 'receive_timestamp', 'sender' , 'message']
    def has_add_permission(self,request):
        return False

class OutboxAdmin(admin.ModelAdmin):
    model = OutboundMessage
    list_display = ['to', 'send_timestamp', send_status_explained, status_explained, 'message', 'external_reference']
    def has_add_permission(self,request):
        return False

admin.site.register(InboundMessage, InboxAdmin)
admin.site.register(OutboundMessage, OutboxAdmin)
