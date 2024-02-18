# registrtaion/templatetags/haspayment_history.py

from django import template
from payment.models import PaymentHistory

register = template.Library()

@register.simple_tag
def get_has_payment_history(value):
    return PaymentHistory.paymenthistorycurrentmgr.get_stallholder_payment_history(value).exists()