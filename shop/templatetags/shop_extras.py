from django import template

register = template.Library()


@register.filter
def star_range(rating):
    return range(round(rating or 0))


@register.filter
def empty_star_range(rating):
    return range(5 - round(rating or 0))
