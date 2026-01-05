from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Возвращает URL-кодированную строку параметров с обновленными значениями.
    Использование: {% param_replace page=page_obj.next_page_number %}
    """
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    return d.urlencode()

@register.simple_tag
def check_selected(current_value, param_value):
    """
    Возвращает 'selected', если значения совпадают.
    Приводит оба значения к строке перед сравнением.
    Использование: {% check_selected item.id request.GET.technique_model %}
    """
    if str(current_value) == str(param_value):
        return 'selected'
    return ''
