# payment/templatetags/haspaymenthistories_tags.py

from django import template
from payment.models import (
    PaymentHistory,
)

register = template.Library()


@register.simple_tag
def get_has_paymenthistories(value):
    """
    Templatetag to provide a boolean answer whether there are any Payment Histories
    Used in the convener payment list
    """
    if value:
        return PaymentHistory.paymenthistorycurrentmgr.filter(payment_status=value).exists()
    else:
        return PaymentHistory.paymenthistorycurrentmgr.all().exists()
