# faq/forms.py

from django import forms
from django.forms import (
    BooleanField,
    Form,
    ModelForm,
    Textarea,
    TextInput,
    CheckboxInput,
    Select,
)
from faq.models import (
    FAQ,
)

class FaqCreateForm(ModelForm):
    """
    Form for creating a new FAQ
    """

    class Meta:
        model = FAQ
        fields = ['location', 'question', 'answer']
        widgets = {
            'location': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;'
            }),
            'question': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 700px;',
                'placeholder': 'FAQ Question'
            }),
            'answer': Textarea(attrs={
                'class': "form-control",
                'style': 'max-width: 700px;',
                'placeholder': 'Please enter the FAQ Answer'
            }),
        }

    def clean_question(self):
        question = self.cleaned_data['question']
        if FAQ.objects.filter(question=question).exists():
            raise forms.ValidationError("This FAQ question has already been created.")
        return question


class FaqUpdateForm(ModelForm):
    """
    Form for updating or amending a FAQ
    """

    class Meta:
        model = FAQ
        fields = ['location', 'question', 'answer', 'is_active']
        widgets = {
            'location': Select(attrs={
                'class': "form-select",
                'style': 'max-width: 300px;'
            }),
            'question': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 700px;',
                'placeholder': 'FAQ Question'
            }),
            'answer': Textarea(attrs={
                'class': "form-control",
                'style': 'max-width: 700px;',
                'placeholder': 'Please enter the FAQ Answer'
            }),
            'is_active': CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


