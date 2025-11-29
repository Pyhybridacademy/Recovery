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