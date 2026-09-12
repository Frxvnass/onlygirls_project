from django import template

from shop.translations import translate

register = template.Library()


@register.simple_tag(takes_context=True)
def t(context, key):
    request = context.get('request')
    lang = request.session.get('language', 'uz') if request else 'uz'
    return translate(key, lang)


@register.filter
def star_range(rating):
    return range(round(rating or 0))


@register.filter
def empty_star_range(rating):
    return range(5 - round(rating or 0))
