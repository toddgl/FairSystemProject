# registration/templatetags/hasopenapplications_tags.py

from django import template
from fairs.models import Fair

register = template.Library()

@register.simple_tag
def has_open_applications():
    return Fair.currentfairmgr.filter(is_open=True).exists()