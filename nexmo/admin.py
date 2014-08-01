# encoding: utf-8

from django.contrib import admin

from .models import (
    Inbox,
    Outbox
)


class InboxAdmin(admin.ModelAdmin):
    model = Inbox
    list_display = ['messageId', 'nexmo_timestamp', 'receive_timestamp', 'message']
    def has_add_permission(self,request):
        return False

class OutboxAdmin(admin.ModelAdmin):
    model = Outbox
    def has_add_permission(self,request):
        return False

admin.site.register(Inbox, InboxAdmin)
admin.site.register(Outbox, OutboxAdmin)
