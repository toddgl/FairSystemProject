# payment/forms.py

from django import forms
from django.forms import (
    Form,
    ChoiceField,
    Select,
)

class PaymentHistoryStatusFilterForm(Form):
    """
    Description: A filter form used in the listing  of Payment Histories.  The PAYMENT_CHOICES are a copy of the ones set
    up on the PaymentHistory Model
    """
    PAYMENT_CHOICES =(
        ("", "Show All"),
        ("Pending",  "Pending"),
        ("Cancelled", "Cancelled"),
        ("Completed", "Completed"),
        ("Failed", "Failed"),
        ("Reconciled", "Reconciled")
    )

    payment_status = ChoiceField(
        choices=PAYMENT_CHOICES,
        label='Payment Status',
        required=False,
        widget=Select(attrs={
            'class': 'form-select',
            'style': 'max-width: 300px;',
        }),
    )
    form_purpose = forms.CharField(widget=forms.HiddenInput(), initial='filter')

