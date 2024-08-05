# payments/templatetags/hassomethingtopay_tag.py

from django import template
from payment.models import PaymentHistory

register = template.Library()

@register.simple_tag
def get_has_something_to_pay(value):
    amount_to_pay = PaymentHistory.objects.get(id=value).amount_to_pay
    if amount_to_pay == 0:
        return False
    else:
        return True