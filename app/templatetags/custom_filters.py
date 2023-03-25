import json

from django import template


register = template.Library()

@register.filter
def to_json(value):
    return json.dumps(value)

@register.filter 
def times(number):
    return range(1, number+1)

@register.filter 
def minus(number):
    return int(number) - 1

@register.filter 
def plus(number):
    return int(number) + 1



