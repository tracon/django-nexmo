from django import forms
from django.core.validators import RegexValidator
from django.utils.timezone import utc


HEX = RegexValidator(regex=r'^[0-9a-fA-F]+$')


class DeliveryForm(forms.Form):
    messageId = forms.CharField(validators=[HEX,])
    status = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(DeliveryForm, self).__init__(*args, **kwargs)

        self.fields['client-ref'] = forms.CharField(required=False)
        self.fields['err-code'] = forms.CharField(required=False)
        self.fields['message-timestamp'] = forms.DateTimeField(input_formats=['%Y-%m-%d %H:%M:%S'])

    def clean(self):
        cleaned_data = super(DeliveryForm, self).clean()

        if 'message-timestamp' in self.cleaned_data:
            self.cleaned_data['message-timestamp'] = self.cleaned_data['message-timestamp'].replace(tzinfo=utc)

        return cleaned_data