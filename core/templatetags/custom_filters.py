# core/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """Divide the value by the argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

# core/templatetags/custom_filters.py - CREATE THIS FILE

# core/templatetags/custom_filters.py

from django import template
from django.utils import timezone
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def timesince_simple(value):
    """Simple timesince filter for notifications"""
    if not value:
        return ""
    
    now = timezone.now()
    diff = now - value
    
    if diff.days > 0:
        return f"{diff.days}d ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours}h ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes}m ago"
    else:
        return "Just now"