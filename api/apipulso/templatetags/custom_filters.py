from django import template

register = template.Library()

@register.filter
def is_true(value):
    return value.strip().lower() == "true"
