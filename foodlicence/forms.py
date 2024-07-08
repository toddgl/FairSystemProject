# foodlicence/forms.py

from django import forms
from django.forms import (
    Form,
    ChoiceField,
    Select,
    DateInput
)

from .models import (
    FoodLicence,
    FoodLicenceBatch
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

class FoodLicenceBatchDateForm(Form):
    """
    Description: a form used in a model on the food licence batch view to update the returned and closed date
    """
    class Meta:
        model = FoodLicenceBatch
        fields = ['date_returned', 'date_closed' ]
        widgets = {
            'date_returned': DateInput(attrs={
                'class': "form-control",
                'readonly': 'readonly'
            }),
            'date_closed': DateInput(attrs={
                'class': "form-control",
                'readonly': 'readonly'
            }),
        }

