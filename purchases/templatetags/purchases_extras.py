from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

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
    """"""
    if not decimal_places:
        return_value = "%g%%" % (value)
    else:
        rounded = round(value, decimal_places)
        return_value = "%g%%" % (rounded)

    return return_value

@register.filter
def numeric2percent(value:float, decimal_places:int = None):
    """"""
    as_percent = value * 100
    if not decimal_places:
        floated = float(as_percent)
        return_value = "%s%%" % (float(as_percent))
    else:
        rounded = round(as_percent, decimal_places)
        return_value = "%s%%" % (rounded)

    return return_value