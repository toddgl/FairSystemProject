# notices/forms.py

from django import forms
from django.forms import (
    ModelForm,
    Textarea,
    TextInput,
    CheckboxInput,
)
from notices.models import (
    Notice
)

class NoticeCreateForm(ModelForm):
    """
    Form for creating a new Notice
    """

    class Meta:
        model = Notice
        fields = ['notice_title', 'notice_content']
        widgets = {
            'notice_title': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 700px;',
                'placeholder': 'Notice Title'
            }),
            'notice_content': Textarea(attrs={
                'class': "form-control",
                'style': 'max-width: 700px;',
                'placeholder': 'Please enter the notice content'
            }),
        }

    def clean_title(self):
        notice_title = self.cleaned_data['notice_title']
        if Notice.objects.filter(notice_title=notice_title).exists():
            raise forms.ValidationError("This Notice Title has already been created.")
        return notice_title


class NoticeUpdateForm(ModelForm):
    """
    Form for updating or amending a Notice
    """

    class Meta:
        model = Notice
        fields = ['notice_title', 'notice_content', 'is_active']
        widgets = {
            'notice_title': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 700px;',
                'placeholder': 'Notice Title'
            }),
            'notice_content': Textarea(attrs={
                'class': "form-control",
                'style': 'max-width: 700px;',
                'placeholder': 'Please enter the notice content'
            }),
            'is_active': CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
