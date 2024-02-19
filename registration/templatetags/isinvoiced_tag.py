# registrtaion/templatetags/isinvoiced_tag.py

from django import template
from registration.models import (
    StallRegistration
)
register = template.Library()

@register.simple_tag
def get_is_invoiced(value):
    return StallRegistration.registrationinvoicedmgr.filter(id=value).exists()