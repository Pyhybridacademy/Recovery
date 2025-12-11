# core/signals.py - CREATE THIS FILE

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SiteSettings
from .utils import clear_site_settings_cache

@receiver(post_save, sender=SiteSettings)
def clear_cache_on_save(sender, instance, **kwargs):
    """Clear site settings cache when settings are updated"""
    clear_site_settings_cache()