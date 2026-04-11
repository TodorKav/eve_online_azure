from django import template

register = template.Library()

@register.filter
def int_separator(value):
    return value.replace(",", " ")
