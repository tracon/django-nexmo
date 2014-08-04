# encoding: utf-8

from .libpynexmo.nexmomessage import NexmoMessage

from django.conf import settings
from django.db import models, connection
import django.dispatch

message_received = django.dispatch.Signal(providing_args=["messageId"])

class InboundMessageFragment(models.Model):
    
    messageId = models.CharField(
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

    def save(self, *args, **kwargs):
        # Needed to make Nexmos api happy, as it tests the callback url with no parameters (and expects 200 OK) when you configure it.
        if self.messageId is None:
            return True
        else:
            if self.concat_ref:
                ret_val = super(InboundMessageFragment, self).save(*args, **kwargs)
                pieces = InboundMessageFragment.objects.filter(concat_ref=self.concat_ref).order_by('concat_part')
                if connection.vendor != "sqlite":
                    pieces = pieces.distinct("concat_part")
                if len(pieces) >= self.concat_total:
                    message_pieces = pieces.values_list('message', flat=True)
                    message = u"".join(message_pieces)
                    normal = InboundMessage(messageId=self.messageId, message=message, sender=self.sender, nexmo_timestamp=self.nexmo_timestamp, receive_timestamp=django.utils.timezone.now())
                    normal.save()
                    InboundMessageFragment.objects.filter(concat_ref=self.concat_ref).delete()

            else:
                normal = InboundMessage(messageId=self.messageId, message=self.message, sender=self.sender, nexmo_timestamp=self.nexmo_timestamp, receive_timestamp=django.utils.timezone.now())
                ret_val = normal.save()

        return ret_val

    def __unicode__(self):
        return self.message

    class Meta:
        verbose_name = u'Inbound Message Fragment'
        verbose_name_plural = u'Inbound Message Fragments'

class InboundMessage(models.Model):

    messageId = models.CharField(
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

        if self.messageId:
            message_received.send(sender=self.__class__, messageId=self.messageId)

        return ret_val

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
        auto_now=True,
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

    status_timestamp = models.DateTimeField(
        verbose_name=u'Statuksen saantihetki',
        null=True,
        blank=True,
    )

    external_reference = models.CharField(
        max_length=255,
        verbose_name=u'Ulkoinen viittaus',
        help_text=u'Viittaus tapahtumaan/ohjelmaan/äänestykseen/whatnot.'
    )

    def send(self, *args, **kwargs):
        msg = OutboundMessage(message=self.message,to=self.to,external_reference=self.external_reference)
        msg.save()
        params = {
            'api_key': settings.NEXMO_USERNAME,
            'api_secret': settings.NEXMO_PASSWORD,
            'from': settings.NEXMO_FROM,
            'to': self.to,
            'client-ref': msg.id,
            'status-report-req': 1,
            'text': self.message.encode('utf-8'),
        }

        sms = NexmoMessage(params)
        response = sms.send_request()
        for resp in response['messages']:
            msg.send_status = resp['status'];
            msg.save();
            if resp['status'] == u'0':
                delivery = DeliveryStatusFragment(message=msg, messageId=resp['message-id'])
                delivery.save()
            if resp['status'] == u'1':
                # Throttled. Sending signal to retry.
                raise RetryError("Throttled")
        return response

    class Meta:
        verbose_name = u'Outbound Message'
        verbose_name_plural = u'Outbound Messages'

class DeliveryStatusFragment(models.Model):

    message = models.ForeignKey(OutboundMessage)

    messageId = models.CharField(
        max_length=255,
        verbose_name=u"Nexmon yksilöintitieto",
        help_text=u"Nexmo erittelee eri viestit tällä yksilöintitiedolla.",
    )

    error_code = models.IntegerField(
        verbose_name=u'Viestin status',
        null=True,
        blank=True,
    )

    status_timestamp = models.DateTimeField(
        verbose_name=u'Statuksen saantihetki',
        null=True,
        blank=True,
    )




class RetryError(Exception):
    """Exception raised for errors which needs trying again after short short wait.

    Attributes:
        msg  -- explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg
