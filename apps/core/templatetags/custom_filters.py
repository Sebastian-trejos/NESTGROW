from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def percentage(value, total):
    if total == 0:
        return 0
    return int((value / total) * 100)


@register.simple_tag
def milo_emotion(score):
    """Returns Milo's mood based on score."""
    if score >= 90:
        return 'super_happy'
    elif score >= 70:
        return 'happy'
    elif score >= 50:
        return 'neutral'
    else:
        return 'encouraging'
