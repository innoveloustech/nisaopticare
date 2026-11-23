from django import template
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag
def querystring(get, key, value):
    dict_ = get.copy()
    dict_[key] = value
    return dict_.urlencode()
