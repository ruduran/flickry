from django import template
register = template.Library()


@register.filter
def index(col, i):
    return col[int(i)]
