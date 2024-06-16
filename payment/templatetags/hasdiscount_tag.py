# payments/templatetags/hasdiscount_tag.py

from django import template
from payment.models import DiscountItem

register = template.Library()

@register.simple_tag
def get_has_discount(value):
    return DiscountItem.discountitemmgr.get_registration_discount(value).exists()