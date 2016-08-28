from django.conf.urls import url

from .views import nexmo_delivery, nexmo_message

urlpatterns = [
    url(r'^nexmo/delivery/(?P<key>[a-f0-9]+)/$', nexmo_delivery, name='nexmo_delivery'),
    url(r'^nexmo/message/(?P<key>[a-f0-9]+)/$', nexmo_message, name='nexmo_message'),
]
