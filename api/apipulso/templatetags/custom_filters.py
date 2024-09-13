from django import template

register = template.Library()

@register.filter
def is_true(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return False