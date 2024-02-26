# registrtaion/templatetags/isfoodstall_tag.py

from django import template
from registration.models import (
    StallRegistration
)
register = template.Library()

@register.simple_tag
def get_is_foodstall(value):
    return StallRegistration.sellingfoodmgr.filter(id=value).exists()