# registration/templatetags/hasunallocatedsites_tags.py

from django import template
from fairs.models import SiteAllocation

from registration.models import AdditionalSiteRequirement

register = template.Library()

@register.simple_tag
def get_has_unallocated_sites(value):
    siteallocation_count = SiteAllocation.currentallocationsmgr.filter(stall_registration_id= value).count()
    additionalsites_count = AdditionalSiteRequirement.additionalsiterequirementmgr.filter_by_stallregistration(value).count()
    if (additionalsites_count +2) > siteallocation_count:
        return True
    else:
        return False