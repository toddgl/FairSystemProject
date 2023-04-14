# fairs/templatetags/define_action.py

from django import template
register = template.Library()

@register.simple_tag
def define(val=None):
  return val