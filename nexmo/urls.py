from django.conf.urls import patterns, url


urlpatterns = patterns(
    'nexmo.views',
    url(r'^nexmo/delivery/(?P<key>[a-f0-9]+)/$', 'nexmo_delivery', name='nexmo_delivery'),
    url(r'^nexmo/message/(?P<key>[a-f0-9]+)/$', 'nexmo_message', name='nexmo_message'),
)
