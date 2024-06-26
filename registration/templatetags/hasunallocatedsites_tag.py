# registration/templatetags/hasunallocatedsites_tags.py

from django import template
from fairs.models import SiteAllocation

from registration.models import AdditionalSiteRequirement

register = template.Library()

@register.simple_tag
def get_has_unallocated_sites(value):
    """
    Templatetag to provide a boolean answer whether a particular stall registration has unallocated site requests or not.
    Used in the convener stall registration list and site allocations
    """
    siteallocation_count = SiteAllocation.currentallocationsmgr.filter(stall_registration_id= value).count()
    additionalsites_count = AdditionalSiteRequirement.additionalsiterequirementmgr.filter_by_stallregistration(value).count()
    if (additionalsites_count +2) > siteallocation_count:
        return True
    else:
        return False

@register.simple_tag
def get_number_unallocated_sites(value):
    """
    Templatetag to give a count of unallocated sites used in the convener stall registration list and site allocations
    """
    siteallocation_count = SiteAllocation.currentallocationsmgr.filter(stall_registration_id= value).count()
    additionalsites_count = AdditionalSiteRequirement.additionalsiterequirementmgr.filter_by_stallregistration(value).count()
    unallocated_sites = (2 + additionalsites_count * 2) - siteallocation_count
    return unallocated_sites
