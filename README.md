# django-nexmo

`django-nexmo` is a tiny Django app to send sms using the Nexmo provider.

## Installation

Installation using pip is simple:

    $ pip install django-nexmo

Add the `nexmo` app to your installed applications:

```python
INSTALLED_APPS = (
    …
    'nexmo',
    …
)
```

and, sync your db
    
    $ ./manage.py syncdb

## Configuration

You need to add a few lines in your `settings.py` file for django-nexmo to work:

```python
NEXMO_USERNAME = 'username'
NEXMO_PASSWORD = 'password'
NEXMO_FROM = 'Name or phone'
NEXMO_INBOUND_KEY = '1234567890abcdef'
```

For inbound messages and delivery reports, you need to configure callbacks on your Nexmo account.

Did I mention that you need a [Nexmo account](https://www.nexmo.com/)?
Seems quite obvious to me.


## Basic usage

The `nexmo` app gives you access to a shoot-and-forget shortcut to send text messages easily.

```python
from nexmo import send_message
send_message('+33612345678', 'My sms message body')
```

Is that all? Yes… for now. Messages sent this way aren't saved anywhere and delivery statuses aren't tracked though.

## Typical usage

The `nexmo` app typical usage will be sending messages, tracking delivery process and receiving messages.

Sending messages is little bit harder than basic usage:

```python
from nexmo import OutboundMessage
OutboundMessage.send(message=u'My sms message body', to=u'+123465789', external_reference=u'test')
```
    
or

```python
from nexmo import OutboundMessage
message = OutboundMessage(message=u'My sms message body', to=u'+123465789', external_reference=u'test')   
message.save()
message._send()
```

Note the difference of these two. `send()` is classmethod, `_send()` normal. `_send()` is available for mass operations,
which you probably want to use with celery or similar and save all messages before start sending. Both tracks delivery
statuses, so only calling method differs.

Nexmo allows 5 messages per second by default. If you are throttled, RetryError is raised. Messages and delivery data 
are saved to the database.

External reference allows you to mark messages however you want. If you want to track which app send the message
or which user account was used or whatever you want, you can put it there. You must put something.

If you have inbound number from Nexmo, you can receive text messages. Multi-part messages are supported. Inbound
messages sends signal which you can catch f.ex. for processing hot words:

```python
from django.dispatch import receiver
from nexmo.models import InboundMessage

@receiver(message_received, sender=InboundMessage)
def my_handler(sender, **kwargs):
    message = InboundMessage.objects.filter(messageId=messageId)
    ...
```

All text messages can be read from admin-panel.

## Advanced usage

`django-nexmo` embeds [libpynexmo by Marco Londero](https://github.com/marcuz/libpynexmo).
Therefore, you can import and use the `NexmoMessage` class to manually forge
requests to the Nexmo API. To fetch your balance for example:

```python
from nexmo.libpynexmo.nexmomessage import NexmoMessage

params = {
    'api_key': settings.NEXMO_USERNAME,
    'api_secret': settings.NEXMO_PASSWORD,
    'type': 'balance',
}
sms = NexmoMessage(params)
response = sms.send_request()
```


## Handling callbacks

Nexmo can call one of your urls to send further details about a text message processing or deliver inbound message.

`django-nexmo` provides support for both of the cases.

In your main `urls.py` file:

```python
urlpatterns = patterns('',
    …
    url(r'^nexmo/', include('nexmo.urls')),
    …
)
```

This will declare a callback view accessible through the
`http://your-site.url/nexmo/delivery/NEXMO_INBOUND_KEY/` url.

Copy this url and paste it in the "Callback URL" section of your "API settings"
section of your Nexmo.com account and select POST in drop-down menu. Remember to replace NEXMO_INBOUND_KEY to whatever
you set to settings. Hex numbers are allowed.

Inbound text messages are received the same way. Receiving messages is accessible through the
`http://your-site.url/nexmo/message/NEXMO_INBOUND_KEY/` url.

Copy this url and and paste it in the "Numbers" section of your Nexmo.com account. You will need to buy number
from Nexmo for this, and it will cost you monthly fee of few dollars (in U.S.A: $0.90/month, in Finland €3.00/month)

## Translations

English (default) and Finnish is available for localization. If you want to translate status messages to different language, in `nexmo/locale`
copy folder `fi` to new with desired language code. Then, translate the `nexmo/locale/<new language code>/LC_MESSAGES/django.po`. After that
use command `msgfmt -o django.mo django.po` to compile it, you need gettext installed for that. Unfortunatelly we can't use django to create
and compile these translations as it doesn't find any strings to put in .po-file (I don't know why). After that you need to add several things
to your settings.py:

```python
MIDDLEWARE_CLASSES = (
    ...
    'django.middleware.locale.LocaleMiddleware',
    ...
)

LANGUAGES = (
    ('fi', _('Finnish')),
    ('en', _('English')),
    # and all the other languages you have translated.
)

LANGUAGE_CODE = 'fi' # or which language you want to use.

USE_L10N = True
USE_L18N = True
```