# reports/templatetags/getpower_trestle_tag.py

from django import template
from registration.models import (
    StallRegistration
)

register = template.Library()


@register.simple_tag
def get_has_power(siteregistration):
    # Preserve the existing power check.
    has_power = StallRegistration.registrationcurrentmgr.has_power(
        siteregistration
    )

    # Also recognise power recorded through the new power-source field.
    power_source = (
        StallRegistration.objects
        .filter(pk=siteregistration)
        .values_list("power_source", flat=True)
        .first()
    )

    return has_power or power_source in {"fair", "generator"}


@register.simple_tag
def get_has_trestles(siteregistration):
    """
    Returns boolean response to whether the site registration includes Testles

    """
    return StallRegistration.registrationcurrentmgr.has_trestles(siteregistration)

@register.simple_tag
def get_is_generator(siteregistration):
    """
    Return True when the registration's power source is a generator.
    """
    power_source = (
        StallRegistration.objects
        .filter(pk=siteregistration)
        .values_list("power_source", flat=True)
        .first()
    )

    return power_source == "generator"
