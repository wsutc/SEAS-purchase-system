import re

from django import template
from django.apps import AppConfig
from django.contrib.humanize.templatetags.humanize import intcomma
from django.shortcuts import redirect
from django.template.defaultfilters import stringfilter
from django.urls import reverse
from django.utils.html import conditional_escape, mark_safe
from furl import furl

register = template.Library()


@register.filter
def currency(value: float, currency: str = "USD"):
    """Format number as currency

    Currently only supports USD which is default"""
    match currency:
        case "USD":
            dollars = round(float(value), 2)
            return_value = "${}{}".format(
                intcomma(int(dollars)), ("%0.2f" % dollars)[-3:]
            )

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

    decimals = 2 if decimals < 2 else decimals

    dollars = prepare_for_currency(value, decimals)

    string = """
        <table style="width: 100%">
            <td align="left">$</td>
            <td align="right">{value:,.{prec}f}</td>
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

    if floated is not False:
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
        return_value = f"{value:g}%"
    else:
        # rounded = round(value, decimal_places)
        # return_value = "%g%%" % (rounded)
        if value.is_integer():
            return_value = f"{value:g}%"
        else:
            value = round(value, decimal_places)
            return_value = f"{value:g}%"

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
        return_value = f"{as_percent:g}%"
        # return_value = "%s%%" % (float(as_percent))
    else:
        as_percent = round(as_percent, decimal_places)
        # value = float("{0:{1}f}".format(value, decimal_places+2))
        return_value = f"{as_percent:g}%"
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

    tag = f'<a href="{href}">{value}</a>'

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


@register.filter(needs_autoescape=True)
def urlizeobject(object, autoescape=True):
    """Create a link for an object using it's `get_absolute_url` method, if it has one.

    :param object: The object/model to create a link for
    :type object: models.Model
    :return: If <object> has a `get_absolute_url` method, return a link tag in the form '<a href="{{ object.get_absolute_url }}">{{ object }}</a>';
        if no method exists, return {{ object }}.
    :rtype: str, marked safe
    """
    text = str(object)
    try:
        url = object.get_absolute_url()
    except Exception:
        return text
    else:
        tag = f'<a href="{url}">{text}</a>'

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
