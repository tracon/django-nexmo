# encoding: utf-8

from .libpynexmo.nexmomessage import NexmoMessage

from django.conf import settings
from django.db import models, connection
from django.utils.translation import ugettext as _
import django.dispatch

message_received = django.dispatch.Signal(providing_args=["nexmo_message_id"])

class InboundMessageFragment(models.Model):
    
    nexmo_message_id = models.CharField(
        max_length=255,
        verbose_name=_("Nexmos identification"),
        help_text=_("Nexmo identifies different messages with this identification."),
    )

    sender = models.CharField(
        max_length=255,
        verbose_name=_("Sender"),
    )

    nexmo_timestamp = models.DateTimeField(
        verbose_name=_('Message receive time (nexmo)'),
        null=True,
        blank=True,
    )

    receive_timestamp = models.DateTimeField(
        verbose_name=_('Message receive time (local)'),
        auto_now=True,
    )

    message = models.TextField(
        blank=True,
        verbose_name=_('Text message'),
    )

    concat_ref = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Multi-part message identification"),
        help_text=_("Nexmo identifies different message parts with this identification"),
    )

    concat_part = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("Multi-part message sequence number"),
    )

    concat_total = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("Multi-part message total amount of pieces."),
    )

    def __unicode__(self):
        return self.message

    class Meta:
        verbose_name = _('Inbound Message Fragment')
        verbose_name_plural = _('Inbound Message Fragments')

class InboundMessage(models.Model):

    nexmo_message_id = models.CharField(
        max_length=255,
        verbose_name=_("Nexmos identification"),
        help_text=_("Nexmo identifies different messages with this identification."),
    )

    sender = models.CharField(
        max_length=255,
        verbose_name=_("Sender"),
    )

    nexmo_timestamp = models.DateTimeField(
        verbose_name=_('Message receive time (nexmo)'),
        null=True,
        blank=True,
    )

    receive_timestamp = models.DateTimeField(
        verbose_name=_('Message receive time (local)'),
        null=True,
        blank=True,
    )

    message = models.TextField(
        blank=True,
        verbose_name=_('Text message'),
    )

    def save(self, *args, **kwargs):
        ret_val = super(InboundMessage, self).save(*args, **kwargs)

        if self.nexmo_message_id:
            message_received.send(sender=self.__class__, nexmo_message_id=self.nexmo_message_id)

        return ret_val

    @classmethod
    def new_message(cls, *args, **kwargs):
        # Needed to make Nexmos api happy, as it tests the callback url with no parameters (and expects 200 OK) when you configure it.
        if kwargs['nexmo_message_id'] is None:
            return True
        else:
            if kwargs['concat_ref']:
                fragment = InboundMessageFragment(
                    nexmo_message_id=kwargs['nexmo_message_id'],
                    message=kwargs['message'],
                    sender=kwargs['sender'],
                    concat_ref=kwargs['concat_ref'],
                    concat_part=kwargs['concat_part'],
                    concat_total=kwargs['concat_total'],
                    nexmo_timestamp=kwargs['nexmo_timestamp'],
                    receive_timestamp=django.utils.timezone.now(),
                )
                fragment.save()
                pieces = InboundMessageFragment.objects.filter(concat_ref=kwargs['concat_ref']).order_by('concat_part')
                if connection.vendor != "sqlite":
                    pieces = pieces.distinct("concat_part")
                if len(pieces) >= kwargs['concat_total']:
                    message_pieces = pieces.values_list('message', flat=True)
                    message = u"".join(message_pieces)
                    normal = InboundMessage(
                        nexmo_message_id=kwargs['nexmo_message_id'],
                        message=message,
                        sender=kwargs['sender'],
                        nexmo_timestamp=kwargs['nexmo_timestamp'],
                        receive_timestamp=django.utils.timezone.now(),
                    )
                    normal.save()
                    InboundMessageFragment.objects.filter(concat_ref=kwargs['concat_ref']).delete()

            else:
                normal = InboundMessage(
                    nexmo_message_id=kwargs['nexmo_message_id'],
                    message=kwargs['message'],
                    sender=kwargs['sender'],
                    nexmo_timestamp=kwargs['nexmo_timestamp'],
                    receive_timestamp=django.utils.timezone.now(),
                )
                normal.save()

    def __unicode__(self):
        return self.message

    class Meta:
        verbose_name = _('Inbound Message')
        verbose_name_plural = _('Inbound Messages')

class OutboundMessage(models.Model):
    
    message = models.TextField(
        verbose_name=_('Text message'),
    )
    
    to = models.CharField(
        max_length=50,
        verbose_name=_('Recipient'),
    )

    send_timestamp = models.DateTimeField(
        verbose_name=_('Send time'),
        null=True,
        blank=True,
    )

    send_status = models.IntegerField(
        verbose_name=_('Send status'),
        null=True,
        blank=True,
    )

    status = models.IntegerField(
        verbose_name=_('Message status'),
        default=0,
    )

    sent_pieces = models.IntegerField(
        verbose_name=_('Amount of physical messages'),
        null=True,
        blank=True,
    )

    external_reference = models.CharField(
        max_length=255,
        verbose_name=_('External reference'),
        help_text=_('Refers to event/program/poll/whatever.'),
    )

    @classmethod
    def send(cls, *args, **kwargs):
        message = OutboundMessage(*args, **kwargs)
        message.save()
        return message._send()

    def _send(self, *args, **kwargs):
        if self.message is None:
            return ValueError("No message found.")

        params = {
            'api_key': settings.NEXMO_USERNAME,
            'api_secret': settings.NEXMO_PASSWORD,
            'from': settings.NEXMO_FROM,
            'to': self.to,
            'client-ref': self.id,
            'status-report-req': 1,
            'text': self.message.encode('utf-8'),
        }

        sms = NexmoMessage(params)
        response = sms.send_request()
        self.sent_pieces = response['message-count']
        self.status = 1
        self.send_timestamp = django.utils.timezone.now()
        for resp in response['messages']:
            self.send_status = resp['status']
            self.save()
            if resp['status'] == u'1':
                # Throttled. Sending signal to retry.
                raise RetryError("Throttled")
        return response

    def __unicode__(self):
        return self.message

    class Meta:
        verbose_name = _('Outbound Message')
        verbose_name_plural = _('Outbound Messages')

class DeliveryStatusFragment(models.Model):

    message = models.ForeignKey(OutboundMessage)

    nexmo_message_id = models.CharField(
        max_length=255,
        verbose_name=_("Nexmos identification"),
        help_text=_("Nexmo identifies different messages with this identification."),
    )

    error_code = models.IntegerField(
        verbose_name=_('Error status'),
        null=True,
        blank=True,
    )

    status_msg = models.CharField(
        max_length=50,
        verbose_name=_('Message status'),
        null=True,
        blank=True,
    )

    status_timestamp = models.DateTimeField(
        verbose_name=_('Timestamp of status'),
        null=True,
        blank=True,
    )

    @classmethod
    def handle_message_status(cls, message, *args, **kwargs):
        pieces = DeliveryStatusFragment.objects.filter(message=message)
        message = OutboundMessage.objects.get(pk=message.id)
        if connection.vendor != "sqlite":
            pieces = pieces.distinct("nexmo_message_id")
        if len(pieces) >= message.sent_pieces:
            return_code = 2
            for piece in pieces:
                if piece.error_code != 0:
                    return_code = 3
                    break
            message.status = return_code
            message.save()


class RetryError(RuntimeError):
    """Exception raised for errors which needs trying again after short wait."""
    pass
