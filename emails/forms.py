# emails/forms.py

from django import forms
from django.forms import (
    CharField,
    Form,
    ModelForm,
    ModelChoiceField,
    Select,
    Textarea,
    TextInput
)
from emails.models import (
    Email
)

from fairs.models import (
    Fair
)

from registration.models import (
    CommentType
)


class CreateEmailForm(ModelForm):
    """
    Form for creating a bulk email
    """

    class Meta:
        model = Email
        fields = ['body']
        widgets = {
            'body': Textarea(attrs={
                'class': "form-control",
                'style': 'max-width: 400px;',
                'placeholder': 'Please enter the description'
            }),
        }

class CreateStallholderEmailForm(Form):
    '''
    Form for creating a stallholder email used in the Convener Stallholder Detail View
    '''
    subject_type = ModelChoiceField(
        queryset=CommentType.objects.filter(is_active=True),
        empty_label='Please Select',
        label='Comment Type',
        required=True,
        widget=Select(attrs={'class': "form-select", 'style': 'max-width: 300px;', })
    )
    body = CharField(widget=Textarea(
        attrs={
            "rows":5,
            "cols":20,
            "class":'form-control p-3',
            "placeholder":'Your Message'}
    ))

    form_purpose = forms.CharField(widget=forms.HiddenInput(), initial='email')


class EmailHistoryFilterForm(Form):
    """
    Filter form for listing emails sent  by Fair
    """
    fair = ModelChoiceField(
        queryset=Fair.objects.all(),
        empty_label='Show All',
        label='Fairs',
        required=False,
        widget=Select(attrs={
            'class': 'form-control',
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#email_history_data',
        })
    )
    form_purpose = forms.CharField(widget=forms.HiddenInput(), initial='filter')

