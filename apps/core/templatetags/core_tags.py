from django import template
from django.utils.safestring import mark_safe
from apps.core.utils import calculate_level, get_level_progress, format_xp

register = template.Library()


@register.filter
def level_name(xp):
    level = calculate_level(xp)
    names = {
        1: 'Beginner', 2: 'Elementary', 3: 'Pre-Intermediate',
        4: 'Intermediate', 5: 'Upper-Intermediate', 6: 'Advanced',
        7: 'Proficient', 8: 'Expert', 9: 'Master', 10: 'Legend',
    }
    return names.get(level, 'Beginner')


@register.filter
def xp_progress(xp):
    return get_level_progress(xp)


@register.filter
def format_xp_tag(xp):
    return format_xp(xp)


@register.filter
def user_level(xp):
    return calculate_level(xp)


@register.simple_tag
def progress_ring(percent, size=60, stroke=6, color='#6366f1'):
    radius = (size - stroke * 2) // 2
    circumference = 2 * 3.14159 * radius
    offset = circumference - (percent / 100) * circumference
    return mark_safe(f'''
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" class="progress-ring">
      <circle cx="{size//2}" cy="{size//2}" r="{radius}"
        stroke="#e5e7eb" stroke-width="{stroke}" fill="none"/>
      <circle cx="{size//2}" cy="{size//2}" r="{radius}"
        stroke="{color}" stroke-width="{stroke}" fill="none"
        stroke-dasharray="{circumference:.1f}"
        stroke-dashoffset="{offset:.1f}"
        stroke-linecap="round"
        transform="rotate(-90 {size//2} {size//2})"
        class="progress-ring__circle"/>
    </svg>
    ''')


@register.filter
def multiply(value, arg):
    try:
        return int(value) * int(arg)
    except (TypeError, ValueError):
        return 0


@register.filter
def percentage(part, total):
    try:
        return int((int(part) / int(total)) * 100)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0


@register.filter
def get_item(dictionary, key):
    """Get item from dict by key — used in templates as dict|get_item:key"""
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def duration_format(minutes):
    if minutes < 60:
        return f'{minutes}m'
    hours = minutes // 60
    mins = minutes % 60
    if mins:
        return f'{hours}h {mins}m'
    return f'{hours}h'


@register.filter(name='chr')
def chr_filter(value):
    try:
        return chr(int(value))
    except (TypeError, ValueError):
        return ''


@register.filter
def split(value, arg):
    """Split a string by a delimiter"""
    if not value:
        return []
    return value.split(arg)
