from django.conf.urls import patterns, url


urlpatterns = patterns(
    'nexmo.views',
    url(r'^nexmo/delivery/$', 'nexmo_delivery', name='nexmo_delivery'),
    url(r'^nexmo/message/$', 'nexmo_message', name='nexmo_message'),
)
