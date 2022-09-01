from django import template
from django.utils.html import mark_safe, conditional_escape
from django.template.defaultfilters import stringfilter
from django.contrib.humanize.templatetags.humanize import intcomma

from django.urls import reverse

import re

from furl import furl

register = template.Library()


@register.filter
def currency(value: float, currency: str = "USD"):
    """Format number as currency

    Currently only supports USD which is default"""
    match currency:
        case "USD":
            dollars = round(float(value), 2)
            return_value = "$%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])

            return return_value
        case other:
            return value


@register.filter(needs_autoescape=True)
def usd_accounting(value: float, decimals: int = 2, autoescape=True):
    """Format number as accounting.

    For USD; adds whitespace between $ and numbers to right align digits and left align $.
    """
    if autoescape:
        value = conditional_escape(value)

    dollars = prepare_for_currency(value, decimals)

    string = """
        <table style="width: 100%">
            <td align="left">$</td>
            <td align="right">{value:.{prec}f}</td>
        </table>
    """.format(
        value=dollars, prec=decimals
    )

    return mark_safe(string)


def attempt_float(value) -> bool:
    """Return whether <value> can convert to 'float' type."""
    try:
        output = float(value)
        return output
    except ValueError:
        return False


def prepare_for_currency(value: float, decimals: int = 2) -> str:
    if isinstance(value, str):
        value = re.sub(r"[^0-9.]", "", value)

    floated = attempt_float(value)

    if not floated is False:
        value = floated
    else:
        # Likely 'Money' if not something that can convert to 'float.'
        try:
            value = float(value.amount)
        except TypeError:
            raise

    dollars = round(float(value), decimals)

    return dollars


@register.filter
def percent(value: float, decimal_places: int = None):
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
            value = round(value, decimal_places)
            return_value = "{:g}%".format(value)

    return return_value


@register.filter
def numeric2percent(value: float, decimal_places: int = None):
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
        as_percent = round(as_percent, decimal_places)
        # value = float("{0:{1}f}".format(value, decimal_places+2))
        return_value = "{:g}%".format(as_percent)
        # return_value = "%s%%" % (rounded)

    return return_value


@register.filter
@stringfilter
def camel_case_split(value: str) -> str:
    """Split camel case word into multiple strings"""
    if not value:
        return ""
    split_strings = re.findall(r"[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))", value)

    new_string = ""
    for s in split_strings:
        new_string += s + " "

    new_string = new_string[:-1]  # remove final space because of for loop

    return new_string


@register.filter(needs_autoescape=True)
@stringfilter
def urlizespecify(value: str, href: str, autoescape=True) -> str:
    """Similar to Django's `urlize` but allows for custom text."""
    if autoescape:
        value = conditional_escape(value)

    tag = '<a href="{href}">{text}</a>'.format(text=value, href=href)

    return mark_safe(tag)


@register.filter(needs_autoescape=True)
@stringfilter
def urlizespecifyblank(value: str, href: str, autoescape=True) -> str:
    """Similar to Django's `urlize` but allows for custom text."""
    if autoescape:
        value = conditional_escape(value)

    tag = '<a href="{href}" target="_blank" rel="noopener noreferrer">{text}<i class="fa-solid fa-up-right-from-square" data-fa-transform="shrink-6 up-4"></i></a>'.format(
        text=value, href=href
    )

    return mark_safe(tag)


@register.filter
@stringfilter
def replace(value: str, chars: str) -> str:
    """Replaces any of characters before vertical pipe '|' with character after pipe."""
    old_chars = chars.split("|")
    for i in old_chars[0]:
        value = value.replace(i, old_chars[1])
    return value


@register.simple_tag
def urlquery(path: str, param_name: str, param_val: str) -> str:
    path_reverse = reverse(path)
    fragment = furl(path_reverse)
    fragment.args[param_name] = param_val

    return fragment.url
