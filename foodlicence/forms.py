# foodlicence/forms.py

from django import forms
from django.forms import (
    Form,
    ModelChoiceField,
    Select,
)

from .models import (
    FoodLicence,
)

class FoodlicenceStatusFilterForm(Form):

    zone = ModelChoiceField(
        queryset=FoodLicence.foodlicencecurrentmgr.all(),
        empty_label='Show All',
        label='Licence Status',
        required=False,
        widget=Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#food_Licence_data',
        }),
    )
    class Meta:
        fields = [
            'licence_status',
        ]
    form_purpose = forms.CharField(widget=forms.HiddenInput(), initial='filter')


