from django import template


register = template.Library()

@register.filter
def format_date_key(year, month, day):
    return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
