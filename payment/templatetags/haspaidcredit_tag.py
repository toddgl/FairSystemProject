# payments/templatetags/hasdiscount_tag.py

from django import template
from payment.models import PaymentHistory

register = template.Library()

@register.simple_tag
def get_has_credit(value):
    return PaymentHistory.paymenthistorycurrentmgr.has_credit_amount(value)