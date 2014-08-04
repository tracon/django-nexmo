# encoding: utf-8

from django.contrib import admin

from .models import (
    InboundMessage,
    OutboundMessage,
    DeliveryStatusFragment
)
from .error_messages import (NEXMO_SEND_STATUS, NEXMO_STATUSES, UNKNOWN_STATUS,
                             NEXMO_DELIVERY_STATUS, NEXMO_MESSAGES, UNKNOWN_MESSAGE)

def send_status_explained(obj):
    return NEXMO_SEND_STATUS.get(obj.send_status, UNKNOWN_STATUS)
send_status_explained.short_description = "Lähetysstatus"

def status_explained(obj):
    return NEXMO_DELIVERY_STATUS.get(obj.status, UNKNOWN_MESSAGE)
status_explained.short_description = "Status"

def code_explained(obj):
    return NEXMO_MESSAGES.get(obj.error_code, UNKNOWN_STATUS)
code_explained.short_description = "Välitysstatus"

def status_msg_explained(obj):
    return NEXMO_STATUSES.get(obj.status_msg, UNKNOWN_STATUS)
status_msg_explained.short_description = "Välitysstatus"

class InboxAdmin(admin.ModelAdmin):
    model = InboundMessage
    list_display = ['messageId', 'nexmo_timestamp', 'receive_timestamp', 'sender' , 'message']
    readonly_fields = ['messageId', 'nexmo_timestamp', 'receive_timestamp', 'sender' , 'message']
    def has_add_permission(self,request):
        return False

class DSFAdmin(admin.TabularInline):
    model = DeliveryStatusFragment
    readonly_fields = ['messageId', code_explained, status_msg_explained, 'status_timestamp']
    fields = ['messageId', code_explained, status_msg_explained, 'status_timestamp']
    def has_add_permission(self,request):
        return False

class OutboxAdmin(admin.ModelAdmin):
    model = OutboundMessage
    inlines = [ DSFAdmin, ]
    fields = ['to', 'send_timestamp', send_status_explained, status_explained, 'message', 'sent_pieces', 'external_reference']
    list_display = ['to', 'send_timestamp', send_status_explained, status_explained, 'message', 'external_reference']
    readonly_fields = ['to', 'send_timestamp', send_status_explained, status_explained, 'message', 'external_reference', 'send_status', 'status', 'sent_pieces']
    def has_add_permission(self,request):
        return False

admin.site.register(InboundMessage, InboxAdmin)
admin.site.register(OutboundMessage, OutboxAdmin)
