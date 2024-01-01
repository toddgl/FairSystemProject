# registrtaion/templatetags/hasallocation_tags.py

from django import template
from fairs.models import SiteAllocation

register = template.Library()

@register.simple_tag
def get_has_site_allocation(value):
    return SiteAllocation.currentallocationsmgr.filter(stallholder_id= value,stall_registration__isnull=False).exists()