# core/utils.py - COMPLETE UPDATED FILE

import requests
from decimal import Decimal
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import EmailLog


def get_exchange_rate(from_currency, to_currency):
    """
    Get real-time exchange rate from API
    Falls back to cached rates if API fails
    """
    if from_currency == to_currency:
        return Decimal('1.0')
    
    # Updated fallback rates with all currencies
    fallback_rates = {
        'USD': Decimal('1.0'),
        'EUR': Decimal('0.85'),
        'GBP': Decimal('0.73'),
        'JPY': Decimal('110.0'),
        'CAD': Decimal('1.25'),
        'AUD': Decimal('1.35'),
        'CHF': Decimal('0.92'),
        'CNY': Decimal('6.45'),
        'INR': Decimal('74.0'),
        'SGD': Decimal('1.35'),
        'HKD': Decimal('7.78'),
        'NZD': Decimal('1.45'),
        'KRW': Decimal('1180.0'),
        'MXN': Decimal('20.0'),
        'BRL': Decimal('5.25'),
        'RUB': Decimal('75.0'),
        'ZAR': Decimal('14.5'),
        'TRY': Decimal('8.5'),
        'SEK': Decimal('8.7'),
        'NOK': Decimal('8.9'),
        'DKK': Decimal('6.3'),
        'PLN': Decimal('3.9'),
        'THB': Decimal('33.0'),
        'IDR': Decimal('14200.0'),
        'MYR': Decimal('4.2'),
        'PHP': Decimal('50.0'),
        'VND': Decimal('23000.0'),
        'NGN': Decimal('410.0'),
        'EGP': Decimal('15.7'),
        'SAR': Decimal('3.75'),
        'AED': Decimal('3.67'),
        'QAR': Decimal('3.64'),
        'KWD': Decimal('0.30'),
        'BHD': Decimal('0.38'),
    }
    
    try:
        # Try to get real-time rates from API
        if hasattr(settings, 'EXCHANGE_RATE_API_URL'):
            response = requests.get(settings.EXCHANGE_RATE_API_URL, timeout=5)
            if response.status_code == 200:
                data = response.json()
                rates = data.get('rates', {})
                
                # Convert from USD base
                from_rate = Decimal(str(rates.get(from_currency, fallback_rates.get(from_currency, 1))))
                to_rate = Decimal(str(rates.get(to_currency, fallback_rates.get(to_currency, 1))))
                
                return to_rate / from_rate if from_rate != 0 else Decimal('1.0')
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
    
    # Use fallback rates
    from_rate = fallback_rates.get(from_currency, Decimal('1.0'))
    to_rate = fallback_rates.get(to_currency, Decimal('1.0'))
    
    return to_rate / from_rate if from_rate != 0 else Decimal('1.0')


def convert_amount(amount, from_currency, to_currency):
    """
    Convert amount from one currency to another
    """
    if from_currency == to_currency:
        return amount
    
    rate = get_exchange_rate(from_currency, to_currency)
    return amount * rate


def format_currency(amount, currency_code='USD'):
    """
    Format amount with currency symbol
    """
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'CAD': 'C$',
        'AUD': 'A$',
        'CHF': 'CHF',
        'CNY': '¥',
        'INR': '₹',
        'SGD': 'S$',
        'HKD': 'HK$',
        'NZD': 'NZ$',
        'KRW': '₩',
        'MXN': '$',
        'BRL': 'R$',
        'RUB': '₽',
        'ZAR': 'R',
        'TRY': '₺',
        'SEK': 'kr',
        'NOK': 'kr',
        'DKK': 'kr',
        'PLN': 'zł',
        'THB': '฿',
        'IDR': 'Rp',
        'MYR': 'RM',
        'PHP': '₱',
        'VND': '₫',
        'NGN': '₦',
        'EGP': 'E£',
        'SAR': '﷼',
        'AED': 'د.إ',
        'QAR': '﷼',
        'KWD': 'د.ك',
        'BHD': '.د.ب',
    }
    
    symbol = symbols.get(currency_code, '$')
    
    # Format number based on currency
    if currency_code in ['JPY', 'KRW', 'IDR', 'VND']:
        # No decimal places for these currencies
        return f"{symbol}{amount:,.0f}"
    else:
        return f"{symbol}{amount:,.2f}"


def send_email_with_log(user, subject, template_name, context, email_type='system'):
    """
    Send email and log the attempt
    """
    try:
        # Render email template
        context['user'] = user
        html_content = render_to_string(template_name, context)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body='',  # Plain text fallback (optional)
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        
        # Log success
        EmailLog.objects.create(
            user=user,
            email_type=email_type,
            subject=subject,
            recipient=user.email,
            success=True
        )
        
        return True
        
    except Exception as e:
        # Log failure
        EmailLog.objects.create(
            user=user,
            email_type=email_type,
            subject=subject,
            recipient=user.email,
            success=False,
            error_message=str(e)
        )
        
        return False


def validate_document(file):
    """
    Validate uploaded documents (KYC, evidence, etc.)
    """
    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size > max_size:
        return False, "File size must be less than 10MB"
    
    # Check file extension
    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx', '.txt']
    import os
    ext = os.path.splitext(file.name)[1].lower()
    
    if ext not in allowed_extensions:
        return False, f"File type {ext} not allowed. Use: {', '.join(allowed_extensions)}"
    
    return True, "Valid"


def generate_transaction_reference():
    """
    Generate unique transaction reference
    """
    import uuid
    return f"TXN{str(uuid.uuid4())[:12].upper()}"


def calculate_deposit_amount(case):
    """
    Calculate required deposit based on case amount and plan
    """
    if not case.payment_plan:
        return Decimal('0.00')
    
    if case.payment_plan.fixed_deposit:
        return case.payment_plan.fixed_deposit
    
    percentage = case.payment_plan.deposit_percentage
    return (case.amount_lost * percentage) / Decimal('100')


def get_case_statistics(user):
    """
    Get comprehensive statistics for a user's cases
    """
    from django.db.models import Sum, Count, Q
    from .models import ScamCase, RecoveryTransaction
    
    cases = ScamCase.objects.filter(user=user)
    
    total_lost = cases.aggregate(total=Sum('amount_lost'))['total'] or Decimal('0')
    total_recovered = RecoveryTransaction.objects.filter(
        case__user=user
    ).aggregate(total=Sum('amount_recovered'))['total'] or Decimal('0')
    
    # Calculate recovery rate
    recovery_rate = 0
    if total_lost > 0:
        recovery_rate = (total_recovered / total_lost) * 100
    
    return {
        'total_cases': cases.count(),
        'active_cases': cases.exclude(status__in=['completed', 'rejected']).count(),
        'completed_cases': cases.filter(status='completed').count(),
        'rejected_cases': cases.filter(status='rejected').count(),
        'total_lost': total_lost,
        'total_recovered': total_recovered,
        'recovery_rate': round(recovery_rate, 2),
    }


def notify_admins_new_case(case):
    """
    Notify admins when a new case is submitted
    """
    from django.contrib.auth import get_user_model
    from .models import Notification
    
    User = get_user_model()
    admins = User.objects.filter(user_type='admin')
    
    for admin in admins:
        Notification.objects.create(
            user=admin,
            title='New Case Submitted',
            message=f'New case {case.case_id} submitted by {case.user.username}. Amount: {format_currency(case.amount_lost, case.currency)}',
            notification_type='system'
        )


def check_kyc_required(user, action='withdrawal'):
    """
    Check if KYC is required for specific actions
    """
    if action == 'withdrawal' and hasattr(settings, 'KYC_REQUIRED_FOR_WITHDRAWAL'):
        return settings.KYC_REQUIRED_FOR_WITHDRAWAL and not user.is_kyc_verified
    
    if action == 'case_submission' and hasattr(settings, 'KYC_REQUIRED_FOR_CASE_SUBMISSION'):
        return settings.KYC_REQUIRED_FOR_CASE_SUBMISSION and not user.is_kyc_verified
    
    return False


def get_currency_choices_grouped():
    """
    Return currencies grouped by regions for better dropdown organization
    """
    return {
        'Major Currencies': [
            ('USD', 'US Dollar ($)'),
            ('EUR', 'Euro (€)'),
            ('GBP', 'British Pound (£)'),
            ('JPY', 'Japanese Yen (¥)'),
            ('CHF', 'Swiss Franc (CHF)'),
        ],
        'Americas': [
            ('CAD', 'Canadian Dollar (C$)'),
            ('MXN', 'Mexican Peso ($)'),
            ('BRL', 'Brazilian Real (R$)'),
        ],
        'Asia Pacific': [
            ('AUD', 'Australian Dollar (A$)'),
            ('CNY', 'Chinese Yuan (¥)'),
            ('INR', 'Indian Rupee (₹)'),
            ('SGD', 'Singapore Dollar (S$)'),
            ('HKD', 'Hong Kong Dollar (HK$)'),
            ('NZD', 'New Zealand Dollar (NZ$)'),
            ('KRW', 'South Korean Won (₩)'),
            ('THB', 'Thai Baht (฿)'),
            ('IDR', 'Indonesian Rupiah (Rp)'),
            ('MYR', 'Malaysian Ringgit (RM)'),
            ('PHP', 'Philippine Peso (₱)'),
            ('VND', 'Vietnamese Đồng (₫)'),
        ],
        'Europe': [
            ('SEK', 'Swedish Krona (kr)'),
            ('NOK', 'Norwegian Krone (kr)'),
            ('DKK', 'Danish Krone (kr)'),
            ('PLN', 'Polish Złoty (zł)'),
            ('RUB', 'Russian Ruble (₽)'),
            ('TRY', 'Turkish Lira (₺)'),
        ],
        'Africa & Middle East': [
            ('ZAR', 'South African Rand (R)'),
            ('NGN', 'Nigerian Naira (₦)'),
            ('EGP', 'Egyptian Pound (E£)'),
            ('SAR', 'Saudi Riyal (﷼)'),
            ('AED', 'UAE Dirham (د.إ)'),
            ('QAR', 'Qatari Riyal (﷼)'),
            ('KWD', 'Kuwaiti Dinar (د.ك)'),
            ('BHD', 'Bahraini Dinar (.د.ب)'),
        ]
    }


def format_amount_by_currency(amount, currency_code):
    """
    Format amount according to currency-specific conventions
    """
    symbol = format_currency(0, currency_code).replace('0.00', '').replace('0', '')
    
    # Currencies that typically don't use decimal places
    no_decimal_currencies = ['JPY', 'KRW', 'IDR', 'VND', 'ISK', 'HUF']
    
    if currency_code in no_decimal_currencies:
        formatted_amount = f"{amount:,.0f}"
    else:
        formatted_amount = f"{amount:,.2f}"
    
    return f"{symbol}{formatted_amount}"


def get_currency_info(currency_code):
    """
    Get detailed information about a currency
    """
    currency_info = {
        'USD': {'name': 'US Dollar', 'symbol': '$', 'decimals': 2},
        'EUR': {'name': 'Euro', 'symbol': '€', 'decimals': 2},
        'GBP': {'name': 'British Pound', 'symbol': '£', 'decimals': 2},
        'JPY': {'name': 'Japanese Yen', 'symbol': '¥', 'decimals': 0},
        'CAD': {'name': 'Canadian Dollar', 'symbol': 'C$', 'decimals': 2},
        'AUD': {'name': 'Australian Dollar', 'symbol': 'A$', 'decimals': 2},
        'CHF': {'name': 'Swiss Franc', 'symbol': 'CHF', 'decimals': 2},
        'CNY': {'name': 'Chinese Yuan', 'symbol': '¥', 'decimals': 2},
        'INR': {'name': 'Indian Rupee', 'symbol': '₹', 'decimals': 2},
        'SGD': {'name': 'Singapore Dollar', 'symbol': 'S$', 'decimals': 2},
        'HKD': {'name': 'Hong Kong Dollar', 'symbol': 'HK$', 'decimals': 2},
        'NZD': {'name': 'New Zealand Dollar', 'symbol': 'NZ$', 'decimals': 2},
        'KRW': {'name': 'South Korean Won', 'symbol': '₩', 'decimals': 0},
        'MXN': {'name': 'Mexican Peso', 'symbol': '$', 'decimals': 2},
        'BRL': {'name': 'Brazilian Real', 'symbol': 'R$', 'decimals': 2},
        'RUB': {'name': 'Russian Ruble', 'symbol': '₽', 'decimals': 2},
        'ZAR': {'name': 'South African Rand', 'symbol': 'R', 'decimals': 2},
        'TRY': {'name': 'Turkish Lira', 'symbol': '₺', 'decimals': 2},
        'SEK': {'name': 'Swedish Krona', 'symbol': 'kr', 'decimals': 2},
        'NOK': {'name': 'Norwegian Krone', 'symbol': 'kr', 'decimals': 2},
        'DKK': {'name': 'Danish Krone', 'symbol': 'kr', 'decimals': 2},
        'PLN': {'name': 'Polish Złoty', 'symbol': 'zł', 'decimals': 2},
        'THB': {'name': 'Thai Baht', 'symbol': '฿', 'decimals': 2},
        'IDR': {'name': 'Indonesian Rupiah', 'symbol': 'Rp', 'decimals': 0},
        'MYR': {'name': 'Malaysian Ringgit', 'symbol': 'RM', 'decimals': 2},
        'PHP': {'name': 'Philippine Peso', 'symbol': '₱', 'decimals': 2},
        'VND': {'name': 'Vietnamese Đồng', 'symbol': '₫', 'decimals': 0},
        'NGN': {'name': 'Nigerian Naira', 'symbol': '₦', 'decimals': 2},
        'EGP': {'name': 'Egyptian Pound', 'symbol': 'E£', 'decimals': 2},
        'SAR': {'name': 'Saudi Riyal', 'symbol': '﷼', 'decimals': 2},
        'AED': {'name': 'UAE Dirham', 'symbol': 'د.إ', 'decimals': 2},
        'QAR': {'name': 'Qatari Riyal', 'symbol': '﷼', 'decimals': 2},
        'KWD': {'name': 'Kuwaiti Dinar', 'symbol': 'د.ك', 'decimals': 3},
        'BHD': {'name': 'Bahraini Dinar', 'symbol': '.د.ب', 'decimals': 3},
    }
    
    return currency_info.get(currency_code, {'name': 'Unknown', 'symbol': '$', 'decimals': 2})


def validate_currency_amount(amount, currency_code):
    """
    Validate amount based on currency-specific rules
    """
    currency_info = get_currency_info(currency_code)
    
    if currency_info['decimals'] == 0:
        # For currencies without decimals, amount should be whole number
        if amount % 1 != 0:
            return False, f"{currency_info['name']} amounts must be whole numbers"
    
    if amount <= 0:
        return False, "Amount must be greater than 0"
    
    return True, "Valid"


# Context processor for currency
def currency_context(request):
    """
    Add currency information to all templates
    """
    if request.user.is_authenticated:
        return {
            'user_currency': request.user.preferred_currency,
            'currency_symbol': request.user.get_currency_symbol(),
            'currency_info': get_currency_info(request.user.preferred_currency),
        }
    return {
        'user_currency': 'USD',
        'currency_symbol': '$',
        'currency_info': get_currency_info('USD'),
    }

# core/utils.py - CREATE THIS FILE

from .models import SiteSettings
from django.core.cache import cache

def get_site_settings():
    """Get site settings with caching"""
    cache_key = 'site_settings'
    settings = cache.get(cache_key)
    
    if not settings:
        settings = SiteSettings.load()
        cache.set(cache_key, settings, timeout=60*60)  # Cache for 1 hour
    
    return settings

def clear_site_settings_cache():
    """Clear site settings cache"""
    cache.delete('site_settings')

def get_site_name():
    """Get site name with fallback"""
    try:
        return get_site_settings().site_name
    except:
        return 'RecoveryPro'

def get_logo_url():
    """Get logo URL with fallback to default"""
    try:
        settings = get_site_settings()
        if settings.logo:
            return settings.logo.url
    except:
        pass
    return '/static/images/logo.png'  # Fallback path

def get_favicon_url():
    """Get favicon URL"""
    try:
        settings = get_site_settings()
        if settings.favicon:
            return settings.favicon.url
    except:
        pass
    return '/static/images/favicon.ico'

def get_contact_info():
    """Get all contact information"""
    try:
        settings = get_site_settings()
        return {
            'email': settings.contact_email,
            'phone': settings.contact_phone,
            'support_email': settings.support_email,
            'sales_email': settings.sales_email,
            'address': settings.get_full_address(),
            'business_hours': settings.business_hours,
        }
    except:
        return {
            'email': 'support@recoverypro.com',
            'phone': '+1 (555) 123-4567',
            'support_email': 'support@recoverypro.com',
            'sales_email': 'sales@recoverypro.com',
            'address': '123 Main Street, New York, NY 10001',
            'business_hours': 'Monday - Friday: 9am - 6pm EST',
        }