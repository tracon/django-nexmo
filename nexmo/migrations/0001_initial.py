# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryStatusFragment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nexmo_message_id', models.CharField(help_text='Nexmo identifies different messages with this identification.', max_length=255, verbose_name='Nexmos identification')),
                ('error_code', models.IntegerField(null=True, verbose_name='Error status', blank=True)),
                ('status_msg', models.CharField(max_length=50, null=True, verbose_name='Message status', blank=True)),
                ('status_timestamp', models.DateTimeField(null=True, verbose_name='Timestamp of status', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='InboundMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nexmo_message_id', models.CharField(help_text='Nexmo identifies different messages with this identification.', max_length=255, verbose_name='Nexmos identification')),
                ('sender', models.CharField(max_length=255, verbose_name='Sender')),
                ('nexmo_timestamp', models.DateTimeField(null=True, verbose_name='Message receive time (nexmo)', blank=True)),
                ('receive_timestamp', models.DateTimeField(null=True, verbose_name='Message receive time (local)', blank=True)),
                ('message', models.TextField(verbose_name='Text message', blank=True)),
            ],
            options={
                'verbose_name': 'Inbound Message',
                'verbose_name_plural': 'Inbound Messages',
            },
        ),
        migrations.CreateModel(
            name='InboundMessageFragment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nexmo_message_id', models.CharField(help_text='Nexmo identifies different messages with this identification.', max_length=255, verbose_name='Nexmos identification')),
                ('sender', models.CharField(max_length=255, verbose_name='Sender')),
                ('nexmo_timestamp', models.DateTimeField(null=True, verbose_name='Message receive time (nexmo)', blank=True)),
                ('receive_timestamp', models.DateTimeField(auto_now=True, verbose_name='Message receive time (local)')),
                ('message', models.TextField(verbose_name='Text message', blank=True)),
                ('concat_ref', models.CharField(help_text='Nexmo identifies different message parts with this identification', max_length=255, null=True, verbose_name='Multi-part message identification', blank=True)),
                ('concat_part', models.IntegerField(null=True, verbose_name='Multi-part message sequence number', blank=True)),
                ('concat_total', models.IntegerField(null=True, verbose_name='Multi-part message total amount of pieces.', blank=True)),
            ],
            options={
                'verbose_name': 'Inbound Message Fragment',
                'verbose_name_plural': 'Inbound Message Fragments',
            },
        ),
        migrations.CreateModel(
            name='OutboundMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField(verbose_name='Text message')),
                ('to', models.CharField(max_length=50, verbose_name='Recipient')),
                ('send_timestamp', models.DateTimeField(null=True, verbose_name='Send time', blank=True)),
                ('send_status', models.IntegerField(null=True, verbose_name='Send status', blank=True)),
                ('status', models.IntegerField(default=0, verbose_name='Message status')),
                ('sent_pieces', models.IntegerField(null=True, verbose_name='Amount of physical messages', blank=True)),
                ('external_reference', models.CharField(help_text='Refers to event/program/poll/whatever.', max_length=255, verbose_name='External reference')),
            ],
            options={
                'verbose_name': 'Outbound Message',
                'verbose_name_plural': 'Outbound Messages',
            },
        ),
        migrations.AddField(
            model_name='deliverystatusfragment',
            name='message',
            field=models.ForeignKey(to='nexmo.OutboundMessage'),
        ),
    ]
