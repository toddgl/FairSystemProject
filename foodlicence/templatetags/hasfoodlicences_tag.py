# foodlicence/templatetags/hasfoodlicences_tags.py

from django import template
from foodlicence.models import FoodLicence


register = template.Library()

@register.simple_tag
def get_has_foodlicences():
    """
    Templatetag to provide a boolean answer whether there are any foodlicences
    Used in the convener foodlicence list
    """
    foodlicence_exists = FoodLicence.foodlicencecurrentmgr.exists()
    if foodlicence_exists:
        return True
    else:
        return False

@register.simple_tag
def get_number_batched_foodlicences():
    """
    Templatetag to give a count of batched food licences used in the convener foodlicence list
    """
    batched_foodlicence_count = FoodLicence.foodlicencecurrentmgr.filter(licence_status='Batched').count()
    return batched_foodlicence_count
