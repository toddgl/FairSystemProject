# foodlicence/forms.py

from django import forms
from django.forms import (
    Form,
    ChoiceField,
    Select,
)

from .models import (
    FoodLicence,
)

class FoodlicenceStatusFilterForm(Form):
    """
    Description: A filter form used in the listing  of food licences.  The LICENCE_CHOICES are a copy of the ones set
    up on the FoodLicence Model
    """
    LICENCE_CHOICES =(
        ("", "Show All"),
        ("Created",  "Created"),
        ("Batched", "Batched"),
        ("Submitted", "Submitted"),
        ("Rejected", "Rejected"),
        ("Approved", "Approved")
    )

    licence_status = ChoiceField(
        choices=LICENCE_CHOICES,
        label='Licence Status',
        required=False,
        widget=Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 300px;',
        }),
    )
    form_purpose = forms.CharField(widget=forms.HiddenInput(), initial='filter')


