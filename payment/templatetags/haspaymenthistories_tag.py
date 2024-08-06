# payment/templatetags/haspaymenthistories_tags.py

from django import template
from payment.models import (
    PaymentHistory,
)

register = template.Library()


@register.simple_tag
def get_has_paymenthistories():
    """
    Templatetag to provide a boolean answer whether there are any Payment Histories
    Used in the convener payment list
    """
    paymenthistory_exists = PaymentHistory.paymenthistorycurrentmgr.exists()
    if paymenthistory_exists:
        return True
    else:
        return False
