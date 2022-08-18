from django import template
from django.utils.html import mark_safe, conditional_escape
from django.template.defaultfilters import stringfilter
from django.contrib.humanize.templatetags.humanize import intcomma
import re

register = template.Library()

@register.filter
def currency(value:float, currency:str = 'USD'):
    """Format number as currency
    
    Currently only supports USD which is default"""
    match currency:
        case 'USD':
            dollars = round(float(value), 2)
            return_value = "$%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])

            return return_value
        case other:
            return value

@register.filter
def percent(value:float, decimal_places:int = None):
    """Return human-readable percent of input.
    
    E.g. '95.436'|numeric2percent becomes '95.436%'
         '95.436'|numeric2percent:2 becomes '95.44%'
         '95.4'|numeric2percent:2 becomes '95.4%'
    """
    if not decimal_places:
        return_value = "{:g}%".format(value)
    else:
        # rounded = round(value, decimal_places)
        # return_value = "%g%%" % (rounded)
        if value.is_integer():
            return_value = "{:g}%".format(value)
        else:
            value = round(value,decimal_places)
            return_value = "{:g}%".format(value)

    return return_value

@register.filter
def numeric2percent(value:float, decimal_places:int = None):
    """Return human-readable percent of decimal.
    
    E.g. '.086'|numeric2percent becomes '8.6%'
         '.086'|numeric2percent:2 becomes '8.6%'
    """
    as_percent = float(value * 100)
    if not decimal_places:
        # floated = float(as_percent)
        return_value = "{:g}%".format(as_percent)
        # return_value = "%s%%" % (float(as_percent))
    else:
        as_percent = round(as_percent,decimal_places)
        # value = float("{0:{1}f}".format(value, decimal_places+2))
        return_value = "{:g}%".format(as_percent)
        # return_value = "%s%%" % (rounded)

    return return_value

@register.filter
@stringfilter
def camel_case_split(value:str) -> str:
    """Split camel case word into multiple strings"""
    if not value:
        return ''
    split_strings = re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', value)

    new_string = ""
    for s in split_strings:
        new_string += s + " "

    new_string = new_string[:-1]    #remove final space because of for loop

    return new_string

@register.filter(needs_autoescape=True)
@stringfilter
def urlizespecify(value:str, href:str, autoescape=True) -> str:
    """Similar to Django's `urlize` but allows for custom text."""
    if autoescape:
        value = conditional_escape(value)

    tag = '<a href="{href}">{text}</a>'.format(text=value, href=href)

    return mark_safe(tag)

@register.filter(needs_autoescape=True)
@stringfilter
def urlizespecifyblank(value:str, href:str, autoescape=True) -> str:
    """Similar to Django's `urlize` but allows for custom text."""
    if autoescape:
        value = conditional_escape(value)

    tag = '<a href="{href}" target="_blank" rel="noopener noreferrer">{text}<i class="fa-solid fa-up-right-from-square" data-fa-transform="shrink-6 up-4"></i></a>'.format(text=value, href=href)

    return mark_safe(tag)