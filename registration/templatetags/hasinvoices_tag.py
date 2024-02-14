# registrtaion/templatetags/hasinvoices_tag.py

from django import template
from payment.models import Invoice

register = template.Library()

@register.simple_tag
def get_has_invoices(value):
    return Invoice.invoicecurrentmgr.get_stallholder_invoices(value).exists()