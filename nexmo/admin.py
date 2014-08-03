# encoding: utf-8

from django.contrib import admin

from .models import (
    InboundMessage,
    OutboundMessage
)


class InboxAdmin(admin.ModelAdmin):
    model = InboundMessage
    list_display = ['messageId', 'nexmo_timestamp', 'receive_timestamp', 'sender' , 'message']
    def has_add_permission(self,request):
        return False

class OutboxAdmin(admin.ModelAdmin):
    model = OutboundMessage
    def has_add_permission(self,request):
        return False

admin.site.register(InboundMessage, InboxAdmin)
admin.site.register(OutboundMessage, OutboxAdmin)
