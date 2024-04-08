# payments/templatetags/adddaystodate_tag.py

from datetime import timedelta, timezone, datetime
from django import template

register = template.Library()

@register.simple_tag
def plus_days(value, days):
    if isinstance(value, str):
        value = timezone.datetime.strptime(value, "%Y-%m-%d")
    return (value + timedelta(days=days)).strftime("%d %b %Y")