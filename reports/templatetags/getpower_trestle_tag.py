# reports/templatetags/getpower_trestle_tag.py

from django import template
from registration.models import (
    StallRegistration
)

register = template.Library()

@register.simple_tag
def get_has_trestles(siteregistration):
    """
    Returns boolean response to whether the site registration includes Testles

    """
    return StallRegistration.registrationcurrentmgr.has_trestles(siteregistration)

@register.simple_tag
def get_has_power(siteregistration):
    """
    Returns boolean response to whether the site registration includes power

    """
    return StallRegistration.registrationcurrentmgr.has_power(siteregistration)
