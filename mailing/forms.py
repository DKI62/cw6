from django import forms
from .models import Mailing, Client, Message


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['title', 'status', 'periodicity', 'start_time', 'clients', 'message']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request and self.request.user.is_authenticated:
            self.fields['clients'].queryset = Client.objects.filter(owner=self.request.user)
            self.fields['message'].queryset = Message.objects.filter(owner=self.request.user)


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['full_name', 'email', 'comment']


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']
