# payment/forms.py

from django import forms
from django.forms import (
    ChoiceField,
    DecimalField,
    Form,
    ModelForm,
    NumberInput,
    Select
)

from payment.models import (
    PaymentHistory,
    PaymentType
)

class PaymentHistoryStatusFilterForm(Form):
    """
    Description: A filter form used in the listing  of Payment Histories.  The PAYMENT_CHOICES are a copy of the ones
    set up on the PaymentHistory Model
    """
    PAYMENT_CHOICES = (
        ("", "Show All"),
        ("Pending", "Pending"),
        ("Superceded", "Superceded"),
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

    class Meta:
        fields = [
            'payment_status',
        ]
        labels = {
            'payment_status': 'Select Payment History status',
        }

    form_purpose = forms.CharField(widget=forms.HiddenInput(), initial='filter')

class UpdatePaymentHistoryForm(ModelForm):
    '''
    Used to update Payment history in the Payment History List View
    '''
    class Meta:
        model = PaymentHistory
        fields = [ 'amount_to_pay', 'amount_paid', 'webhook_amount', 'amount_reconciled', 'payment_status', 'payment_type' ]
        widgets = {
            'amount_to_pay': NumberInput(attrs={
                'class': 'form-control',
                'style': 'max-width: 100px;',
            }),
            'amount_paid': NumberInput(attrs={
                'class': "form-control",
                'style': 'max-width: 100px;',
            }),
            'webhook_amount': NumberInput(attrs={
                'class': "form-control",
                'style': 'max-width: 100px;',
            }),
            'amount_reconciled': NumberInput(attrs={
                'class': "form-control",
                'style': 'max-width: 100px;',
            }),
            'payment_status': Select(attrs={
                'class': 'form-select',
                'style': 'max-width: 300px;',
            }),
            'payment_type': Select(attrs={
                'class': 'form-select',
                'style': 'max-width: 300px;',
            }),
        }

