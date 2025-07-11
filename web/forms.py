from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from django import forms
from django.contrib.sites.models import Site

from healthcare.utils import current_site
from user.models import Organization
from web.models import SubscribedUser, Message


class NewsLatterForm(forms.ModelForm):
    class Meta:
        model = SubscribedUser
        fields = ['email']


class MessageForm(forms.ModelForm):
    # description = forms.CharField(widget=forms.Textarea(attrs={'cols': "30", 'rows': "10"}))
    # organization = forms.CharField(max_length=100, widget=forms.HiddenInput())
    # site = forms.CharField(max_length=100, widget=forms.HiddenInput())

    class Meta:
        model = Message
        fields = '__all__'
        exclude = ['is_replied', 'site', 'organisation']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['organization'].initial = current_site().organization
        # self.fields['site'].initial = current_site()
        self.helper = FormHelper()
        self.helper.layout = Layout(
            # 'organization',
            # 'site',
            Row(
                Column('first_name', css_class='input-field col-md-6 mb-0'),
                Column('last_name', css_class='input-field col-md-6 mb-0'),
                css_class='form-row'
            ),
            'subject',
            Row(
                Column('phone', css_class='input-field col-md-6 mb-0'),
                Column('email', css_class='input-field col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('text', css_class='input-field col-md-12 mb-0')
            ),
            Submit('submit', 'Send Message', css_class='thm-btn contact-btn text-center')
        )

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('organization'):
            cleaned_data['organization'] = current_site().organization
        if not cleaned_data.get('site'):
            cleaned_data['site'] = Site.objects.get_current()
        return cleaned_data
