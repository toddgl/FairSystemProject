# reports/forms.py

from django import forms
from django.forms import (
    Select,
    ModelChoiceField,
    Form,
    IntegerField,
    NumberInput,

)

from fairs.models import (
    Event,
    Zone
)

class ReportListFilterForm(Form):
    """
    Filter form for selecting the zone for reporting purposes
    """

    event = ModelChoiceField(
        queryset=Event.currenteventfiltermgr.all(),
        empty_label='Show All',
        label='Event',
        required=False,
        widget=Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#zone_selected',
        })
    )
    zone = ModelChoiceField(
        queryset=Zone.objects.all(),
        empty_label='Show All',
        label='Site Zones',
        required=False,
        widget=Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 300px;',
            'hx-trigger': 'change',
            'hx-post': '.',
            'hx-target': '#zone_selected',
        })
    )
    form_purpose = forms.CharField(widget=forms.HiddenInput(), initial='filter')

    class Meta:
        fields = [
            'zone',
        ]

class StallRegistrationIDFilterForm(Form):
    """
    A filter form to select a stallregistrtion Id
    """
    stallregistration_id = forms.IntegerField(
        label="Select Stall Registration ID",
        widget=NumberInput(attrs={
            'class': "form-control",
            'style': 'max-width: 300px;',
            'placeholder': 'No Stall Registration ID Entered',
        }),
    )
