# core/templatetags/site_tags.py - CREATE THIS FILE

from django import template
from ..utils import get_site_settings, get_logo_url, get_contact_info

register = template.Library()

@register.simple_tag
def site_name():
    return get_site_settings().site_name

@register.simple_tag
def site_logo():
    return get_logo_url()

@register.simple_tag
def site_favicon():
    try:
        settings = get_site_settings()
        if settings.favicon:
            return settings.favicon.url
    except:
        pass
    return '/static/images/favicon.ico'

@register.simple_tag
def contact_phone():
    return get_contact_info()['phone']

@register.simple_tag
def contact_email():
    return get_contact_info()['email']

@register.simple_tag
def company_address():
    return get_contact_info()['address']

@register.simple_tag
def get_theme_colors():
    settings = get_site_settings()
    return {
        'primary': settings.primary_color,
        'secondary': settings.secondary_color,
        'accent': settings.accent_color,
    }

@register.inclusion_tag('includes/social_links.html')
def social_links():
    settings = get_site_settings()
    return {
        'facebook_url': settings.facebook_url,
        'twitter_url': settings.twitter_url,
        'linkedin_url': settings.linkedin_url,
        'instagram_url': settings.instagram_url,
    }