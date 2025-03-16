from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument."""
    return value * arg

@register.filter
def json_loads(value):
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return {}