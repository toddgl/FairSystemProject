# reports/templatetags/gettotalquantity_tag.py

from django import template

register = template.Library()

@register.simple_tag
def totalTrestleCount(arg):
    """
    Usage {{ object | totalTrestleCount arg }}
    Calculates the total trestle quantity from a list of dictionaries.
    """
    return sum(d.get('trestle_quantity', 0) for d in arg)
