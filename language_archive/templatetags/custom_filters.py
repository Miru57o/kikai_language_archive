from django import template

register = template.Library()

@register.filter
def is_equal(value, arg):
    """2つの値が等しいかチェック"""
    return str(value) == str(arg)