# payments/templatetags/payment_tags.py

from django import template
from payment.models import PaymentHistory, Invoice

register = template.Library()

@register.filter
def can_delete_discount(discount_item):
    """
    Returns True if the discount item can be deleted, otherwise False.
    A discount cannot be deleted if any related PaymentHistory has a status of 'Completed' or 'Reconciled'.
    """
    # Find related invoices through stall registration
    related_invoices = Invoice.objects.filter(stall_registration=discount_item.stall_registration)

    # Find related payments linked to those invoices
    related_payments = PaymentHistory.objects.filter(invoice__in=related_invoices)

    # Check if any payment has status "Completed" or "Reconciled"
    return not related_payments.filter(payment_status__in=["Completed", "Reconciled"]).exists()
