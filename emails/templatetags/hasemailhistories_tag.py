# emails/templatetags/hasemailhistories_tags.py

from django import template
from emails.models import (
    Email,
)

register = template.Library()


@register.simple_tag
def get_has_emailhistories():
    """
    Templatetag to provide a boolean answer whether there are any Payment Histories
    Used in the convener payment list
    """
    return Email.emailhistorycurrentmgr.all().exists()
