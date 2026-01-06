from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    return d.urlencode()

@register.simple_tag
def check_selected(current_value, param_value):
    if str(current_value) == str(param_value):
        return 'selected'
    return ''
