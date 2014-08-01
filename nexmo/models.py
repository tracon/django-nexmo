# encoding: utf-8
from datetime import datetime

from django.db import models
import django.dispatch

message_received = django.dispatch.Signal(providing_args=["messageId"])

class InboxTmp(models.Model):
	
	messageId = models.CharField(
		max_length=255,
		verbose_name=u"Nexmon yksilöintitieto",
		help_text=u"Nexmo erittelee eri viestit tällä yksilöintitiedolla.",
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

	concat_part = models.CharField(
		max_length=255,
		null=True,
		blank=True,
		verbose_name=u"Moniosaisen viestin järjestysnumero",
	)

	concat_total = models.CharField(
		max_length=255,
		null=True,
		blank=True,
		verbose_name=u"Moniosaisen viestin palojen kokonaismäärä.",
	)

	def save(self, *args, **kwargs):
		if self.concat_ref:
			ret_val = super(InboxTmp, self).save(*args, **kwargs)
			pieces = InboxTmp.objects.filter(concat_ref=self.concat_ref).order_by('concat_part')
			if len(pieces) >= self.concat_total:
				message_pieces = pieces.values_list('message', flat=True)
				message = u"".join(message_pieces)
				normal = Inbox(messageId=self.messageId, message=message, nexmo_timestamp=self.nexmo_timestamp, receive_timestamp=datetime.now())
				normal.save()

		else:
			normal = Inbox(messageId=self.messageId, message=self.message, nexmo_timestamp=self.nexmo_timestamp, receive_timestamp=datetime.now())
			ret_val = normal.save()

		return ret_val

	def __unicode__(self):
		return self.message

	class Meta:
		verbose_name = u'Inbox'
		verbose_name_plural = u'Inbox'

class Inbox(models.Model):

	messageId = models.CharField(
		max_length=255,
		verbose_name=u"Nexmon yksilöintitieto",
		help_text=u"Nexmo erittelee eri viestit tällä yksilöintitiedolla.",
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
		ret_val = super(Inbox, self).save(*args, **kwargs)

		if self.messageId:
			message_received.send(sender=self.__class__, messageId=self.messageId)

		return ret_val

	def __unicode__(self):
		return self.message

	class Meta:
		verbose_name = u'Inbox'
		verbose_name_plural = u'Inbox'

class Outbox(models.Model):

	def outgoing_message(self):
		return 1

	class Meta:
		verbose_name = u'Outbox'
		verbose_name_plural = u'Outbox'