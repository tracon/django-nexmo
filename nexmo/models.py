# encoding: utf-8

from .libpynexmo.nexmomessage import NexmoMessage

from datetime import tzinfo,timedelta

from django.conf import settings
from django.db import models, connection
import django.dispatch

message_received = django.dispatch.Signal(providing_args=["nexmo_message_id"])

class InboundMessageFragment(models.Model):
    
    nexmo_message_id = models.CharField(
        max_length=255,
        verbose_name=u"Nexmon yksilöintitieto",
        help_text=u"Nexmo erittelee eri viestit tällä yksilöintitiedolla.",
    )

    sender = models.CharField(
        max_length=255,
        verbose_name=u"Lähettäjä",
    )

    nexmo_timestamp = models.DateTimeField(
        verbose_name=u'Viestin vastaanottohetki (nexmo)',
        null=True,
        blank=True,
    )

    receive_timestamp = models.DateTimeField(
        verbose_name=u'Viestin vastaanottohetki (kompassi)',
        auto_now=True,
    )

    message = models.TextField(
        blank=True,
        verbose_name=u'Tekstiviesti',
    )

    concat_ref = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=u"Moniosaisen viestin yksilöintitieto",
        help_text=u"Nexmo erittelee viestin eri osat tällä yksilöintitiedolla.",
    )

    concat_part = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=u"Moniosaisen viestin järjestysnumero",
    )

    concat_total = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=u"Moniosaisen viestin palojen kokonaismäärä.",
    )

    def __unicode__(self):
        return self.message

    class Meta:
        verbose_name = u'Inbound Message Fragment'
        verbose_name_plural = u'Inbound Message Fragments'

class InboundMessage(models.Model):

    nexmo_message_id = models.CharField(
        max_length=255,
        verbose_name=u"Nexmon yksilöintitieto",
        help_text=u"Nexmo erittelee eri viestit tällä yksilöintitiedolla.",
    )

    sender = models.CharField(
        max_length=255,
        verbose_name=u"Lähettäjä",
    )

    nexmo_timestamp = models.DateTimeField(
        verbose_name=u'Viestin vastaanottohetki (nexmo)',
        null=True,
        blank=True,
    )

    receive_timestamp = models.DateTimeField(
        verbose_name=u'Viestin vastaanottohetki (kompassi)',
        null=True,
        blank=True,
    )

    message = models.TextField(
        blank=True,
        verbose_name=u'Tekstiviesti',
    )

    def save(self, *args, **kwargs):
        ret_val = super(InboundMessage, self).save(*args, **kwargs)

        if self.nexmo_message_id:
            message_received.send(sender=self.__class__, nexmo_message_id=self.nexmo_message_id)

        return ret_val

    @classmethod
    def new_message(self, *args, **kwargs):
        # Needed to make Nexmos api happy, as it tests the callback url with no parameters (and expects 200 OK) when you configure it.
        if self.nexmo_message_id is None:
            return True
        else:
            if self.concat_ref:
                fragment = InboundMessageFragment(
                    nexmo_message_id=self.nexmo_message_id,
                    message=self.message,
                    sender=self.sender,
                    concat_ref=self.concat_ref,
                    concat_part=self.concat_part,
                    concat_total=self.concat_total,
                    nexmo_timestamp=self.nexmo_timestamp,
                    receive_timestamp=django.utils.timezone.now(),
                )
                fragment.save()
                pieces = InboundMessageFragment.objects.filter(concat_ref=self.concat_ref).order_by('concat_part')
                if connection.vendor != "sqlite":
                    pieces = pieces.distinct("concat_part")
                if len(pieces) >= self.concat_total:
                    message_pieces = pieces.values_list('message', flat=True)
                    message = u"".join(message_pieces)
                    normal = InboundMessage(
                        nexmo_message_id=self.nexmo_message_id,
                        message=message,
                        sender=self.sender,
                        nexmo_timestamp=self.nexmo_timestamp,
                        receive_timestamp=django.utils.timezone.now(),
                    )
                    normal.save()
                    InboundMessageFragment.objects.filter(concat_ref=self.concat_ref).delete()

            else:
                normal = InboundMessage(
                    nexmo_message_id=self.nexmo_message_id,
                    message=self.message,
                    sender=self.sender,
                    nexmo_timestamp=self.nexmo_timestamp,
                    receive_timestamp=django.utils.timezone.now(),
                )
                normal.save()

    def __unicode__(self):
        return self.message

    class Meta:
        verbose_name = u'Inbound Message'
        verbose_name_plural = u'Inbound Messages'

class OutboundMessage(models.Model):
    
    message = models.TextField(
        verbose_name=u'Tekstiviesti',
    )
    
    to = models.CharField(
        max_length=50,
        verbose_name=u'Vastaanottaja',
    )

    send_timestamp = models.DateTimeField(
        verbose_name=u'Viestin lähetyshetki',
        null=True,
        blank=True,
    )

    send_status = models.IntegerField(
        verbose_name=u'Lähetysstatus',
        null=True,
        blank=True,
    )

    status = models.IntegerField(
        verbose_name=u'Viestin status',
        null=True,
        blank=True,
    )

    sent_pieces = models.IntegerField(
        verbose_name=u'Fyysisten viestien määrä',
        null=True,
        blank=True,
    )

    external_reference = models.CharField(
        max_length=255,
        verbose_name=u'Ulkoinen viittaus',
        help_text=u'Viittaus tapahtumaan/ohjelmaan/äänestykseen/whatnot.'
    )

    @classmethod
    def send(self, *args, **kwargs):
        message = OutboundMessage(message=self.message, to=self.to, external_reference=self.external_reference)
        message.save()
        self._send(message)

    def _send(self, *args, **kwargs):
        if self.message is None:
            return ValueError("No message found.")

        params = {
            'api_key': settings.NEXMO_USERNAME,
            'api_secret': settings.NEXMO_PASSWORD,
            'from': settings.NEXMO_FROM,
            'to': self.to,
            'client-ref': self.message.id,
            'status-report-req': 1,
            'text': self.message.encode('utf-8'),
        }

        sms = NexmoMessage(params)
        response = sms.send_request()
        self.message.sent_pieces = response['message-count']
        self.message.status = 1
        self.message.send_timestamp = django.utils.timezone.now()
        for resp in response['messages']:
            self.message.send_status = resp['status']
            self.message.save()
            if resp['status'] == u'1':
                # Throttled. Sending signal to retry.
                raise RetryError("Throttled")
        return response

    class Meta:
        verbose_name = u'Outbound Message'
        verbose_name_plural = u'Outbound Messages'

class DeliveryStatusFragment(models.Model):

    message = models.ForeignKey(OutboundMessage)

    nexmo_message_id = models.CharField(
        max_length=255,
        verbose_name=u"Nexmon yksilöintitieto",
        help_text=u"Nexmo erittelee eri viestit tällä yksilöintitiedolla.",
    )

    error_code = models.IntegerField(
        verbose_name=u'Viestin virhestatus',
        null=True,
        blank=True,
    )

    status_msg = models.CharField(
        max_length=50,
        verbose_name=u'Viestin status',
        null=True,
        blank=True,
    )

    status_timestamp = models.DateTimeField(
        verbose_name=u'Statuksen saantihetki',
        null=True,
        blank=True,
    )

    def handle_message_status(message):
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
