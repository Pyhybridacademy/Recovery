# core/context_processors.py - ENSURE THIS EXISTS

from .models import UserWallet

def user_wallet(request):
    """Add user wallet to all templates when user is authenticated"""
    if request.user.is_authenticated:
        try:
            wallet = UserWallet.objects.get(user=request.user)
            return {'user_wallet': wallet}
        except UserWallet.DoesNotExist:
            # Create wallet if it doesn't exist
            wallet = UserWallet.objects.create(user=request.user)
            return {'user_wallet': wallet}
    return {'user_wallet': None}

def user_currency(request):
    """
    Add user currency information to all templates
    """
    if request.user.is_authenticated:
        return {
            'user_currency': request.user.preferred_currency,
            'currency_symbol': request.user.get_currency_symbol(),
        }
    return {
        'user_currency': 'USD',
        'currency_symbol': '$',
    }

# core/context_processors.py - CREATE THIS FILE OR ADD TO EXISTING

from .models import SiteSettings

def site_settings(request):
    """Add site settings to all templates"""
    try:
        settings = SiteSettings.load()
        return {
            'site_settings': settings,
            'site_name': settings.site_name,
            'contact_email': settings.contact_email,
            'contact_phone': settings.contact_phone,
            'company_address': settings.get_full_address(),
            'primary_color': settings.primary_color,
            'secondary_color': settings.secondary_color,
            'accent_color': settings.accent_color,
        }
    except:
        # Return default values if settings don't exist
        return {
            'site_settings': None,
            'site_name': 'RecoveryPro',
            'contact_email': 'support@recoverypro.com',
            'contact_phone': '+1 (555) 123-4567',
            'company_address': '123 Main Street, New York, NY 10001, United States',
            'primary_color': '#1e40af',
            'secondary_color': '#0ea5e9',
            'accent_color': '#10b981',
        }

def social_links(request):
    """Add social media links to templates"""
    try:
        settings = SiteSettings.load()
        return {
            'facebook_url': settings.facebook_url,
            'twitter_url': settings.twitter_url,
            'linkedin_url': settings.linkedin_url,
            'instagram_url': settings.instagram_url,
        }
    except:
        return {
            'facebook_url': None,
            'twitter_url': None,
            'linkedin_url': None,
            'instagram_url': None,
        }