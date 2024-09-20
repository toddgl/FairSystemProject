# foodlicence/forms.py

from django import forms
from django.forms import (
    Form,
    ChoiceField,
    DateField,
    Select,
    DateInput,
    ModelForm
)

from .models import (
    FoodLicenceBatch
)
from django.forms.widgets import NumberInput
from datetime import datetime
from django.utils.timezone import make_aware

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



class FoodLicenceBatchUpUpdateForm(ModelForm):
    """
    A form for updating the returned and closed date for FoodLicenceBatch instances.
    """
    class Meta:
        model = FoodLicenceBatch  # Link the form to the FoodLicenceBatch model
        fields = ['date_returned', 'date_closed']  # Fields to be updated
        labels = {
            'date_returned': 'Date a response was received from the SWDC',
            'date_closed':'Date that any action on the Foodlicence ceased'
        }
        widgets = {
            'date_returned': forms.NumberInput(attrs={'type': 'date'}),
            'date_closed': forms.NumberInput(attrs={'type': 'date'}),
        }

    # Optionally, override the init method to make date_closed optional
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_closed'].required = False  # Make date_closed optional



