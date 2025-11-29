# core/views.py - ADD THESE VIEWS TO YOUR EXISTING views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid

from .models import *
from .forms import (
    UserRegistrationForm, EnhancedUserUpdateForm, EnhancedProfileUpdateForm,
    ScamCaseForm, WithdrawalForm, DepositForm, KYCVerificationForm,
    ChangePasswordForm, CustomPasswordResetForm, CustomSetPasswordForm
)



def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def faq(request):
    return render(request, 'faq.html')

def contact(request):
    return render(request, 'contact.html')

def register(request):
    """Enhanced registration with email notification"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create user profile and wallet
            UserProfile.objects.create(user=user)
            UserWallet.objects.create(user=user)
            
            # Send welcome email
            try:
                user.send_email_notification(
                    subject='Welcome to RecoveryPro',
                    template_name='emails/welcome.html',
                    context={'user': user}
                )
                
                # Log email
                EmailLog.objects.create(
                    user=user,
                    email_type='registration',
                    subject='Welcome to RecoveryPro',
                    recipient=user.email,
                    success=True
                )
            except Exception as e:
                EmailLog.objects.create(
                    user=user,
                    email_type='registration',
                    subject='Welcome to RecoveryPro',
                    recipient=user.email,
                    success=False,
                    error_message=str(e)
                )
            
            # Auto-login after registration
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to RecoveryPro.')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'auth/register.html', {'form': form})

@login_required
def kyc_verification(request):
    """KYC submission and status page"""
    # Check if user already has a KYC submission
    latest_kyc = KYCVerification.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        # Don't allow resubmission if approved
        if latest_kyc and latest_kyc.status == 'approved':
            messages.warning(request, 'Your KYC is already approved.')
            return redirect('kyc_verification')
        
        form = KYCVerificationForm(request.POST, request.FILES)
        if form.is_valid():
            kyc = form.save(commit=False)
            kyc.user = request.user
            kyc.status = 'pending'
            kyc.save()
            
            # Create notification
            Notification.objects.create(
                user=request.user,
                title='KYC Submitted',
                message='Your KYC documents have been submitted for review. We will notify you once verified.',
                notification_type='system'
            )
            
            messages.success(request, 'KYC documents submitted successfully! We will review them within 24-48 hours.')
            return redirect('kyc_verification')
    else:
        # Only show form if no pending/approved KYC
        if latest_kyc and latest_kyc.status in ['pending', 'approved']:
            form = None
        else:
            form = KYCVerificationForm()
    
    context = {
        'form': form,
        'latest_kyc': latest_kyc,
    }
    return render(request, 'dashboard/kyc_verification.html', context)


# core/views.py - UPDATE THE DASHBOARD VIEW

from django.utils import timezone
from datetime import datetime

# core/views.py - UPDATE DASHBOARD VIEW

# core/views.py - FIXED DASHBOARD VIEW

from decimal import Decimal

@login_required
def dashboard(request):
    # Get user cases
    user_cases = ScamCase.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Get or create user wallet
    wallet, created = UserWallet.objects.get_or_create(user=request.user)
    
    # Get unread notifications
    notifications = Notification.objects.filter(
        user=request.user, 
        is_read=False
    ).order_by('-created_at')[:10]
    
    # Calculate case statistics - FIXED: Include both 'completed' and 'secured' statuses
    total_cases = ScamCase.objects.filter(user=request.user).count()
    
    # Count completed cases (both 'completed' and 'secured' statuses)
    completed_cases = ScamCase.objects.filter(
        user=request.user, 
        status__in=['completed', 'secured']
    ).count()
    
    # Count active cases (exclude completed and secured statuses)
    active_cases = ScamCase.objects.filter(
        user=request.user
    ).exclude(status__in=['completed', 'secured', 'rejected']).count()
    
    # Calculate total amount lost (for performance metrics)
    total_lost_result = ScamCase.objects.filter(
        user=request.user
    ).aggregate(total=models.Sum('amount_lost'))
    total_lost = total_lost_result['total'] or Decimal('0.00')
    
    # Calculate total recovered from all cases
    total_recovered_result = RecoveryTransaction.objects.filter(
        case__user=request.user
    ).aggregate(total=models.Sum('amount_recovered'))
    total_recovered = total_recovered_result['total'] or Decimal('0.00')
    
    # If no recovery transactions but cases are completed/secured, estimate recovery
    # FIX: Use Decimal instead of float for multiplication
    if total_recovered == Decimal('0.00') and completed_cases > 0:
        # Estimate recovery based on completed cases
        completed_cases_amount_result = ScamCase.objects.filter(
            user=request.user,
            status__in=['completed', 'secured']
        ).aggregate(total=models.Sum('amount_lost'))
        completed_cases_amount = completed_cases_amount_result['total'] or Decimal('0.00')
        
        # Estimate 70% recovery for completed cases - use Decimal arithmetic
        total_recovered = completed_cases_amount * Decimal('0.70')
    
    # Update wallet total recovered (in case it's out of sync)
    if wallet.total_recovered != total_recovered:
        wallet.total_recovered = total_recovered
        wallet.save()
    
    # Current date for template
    current_date = timezone.now()
    
    context = {
        'user': request.user, 
        'cases': user_cases,
        'wallet': wallet,
        'notifications': notifications,
        'case_stats': {
            'total_cases': total_cases,
            'active_cases': active_cases,
            'completed_cases': completed_cases,
            'total_lost': total_lost,
            'recovered_total': total_recovered,
        },
        'current_date': current_date,
    }
    return render(request, 'dashboard/home.html', context)

@login_required
def profile_settings(request):
    """Comprehensive profile settings page"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    wallet, created = UserWallet.objects.get_or_create(user=request.user)
    
    # Initialize all forms
    user_form = EnhancedUserUpdateForm(instance=request.user)
    profile_form = EnhancedProfileUpdateForm(instance=profile)
    password_form = ChangePasswordForm(user=request.user)
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'profile':
            user_form = EnhancedUserUpdateForm(request.POST, instance=request.user)
            profile_form = EnhancedProfileUpdateForm(request.POST, request.FILES, instance=profile)
            
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile_settings')
        
        elif form_type == 'password':
            password_form = ChangePasswordForm(request.user, request.POST)
            
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, request.user)
                
                # Send password change notification
                try:
                    request.user.send_email_notification(
                        subject='Password Changed Successfully',
                        template_name='emails/password_changed.html',
                        context={'user': request.user}
                    )
                except:
                    pass
                
                messages.success(request, 'Password changed successfully!')
                return redirect('profile_settings')
    
    # Get user statistics
    user_cases = ScamCase.objects.filter(user=request.user)
    total_cases = user_cases.count()
    successful_recoveries = RecoveryTransaction.objects.filter(case__user=request.user).count()
    latest_kyc = KYCVerification.objects.filter(user=request.user).first()
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'wallet': wallet,
        'total_cases': total_cases,
        'successful_recoveries': successful_recoveries,
        'profile': profile,
        'latest_kyc': latest_kyc,
    }
    return render(request, 'dashboard/profile_settings.html', context)

@login_required
def case_list(request):
    cases = ScamCase.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'cases/list.html', {'cases': cases})
# core/views.py - UPDATED new_case view

@login_required
def new_case(request):
    if request.method == 'POST':
        form = ScamCaseForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    case = form.save(commit=False)
                    case.user = request.user
                    case.save()
                    
                    # Handle file uploads
                    files = request.FILES.getlist('evidence_files')
                    for file in files:
                        EvidenceFile.objects.create(
                            case=case,
                            file=file,
                            file_type=file.content_type,
                            description=f"Evidence file for case {case.case_id}"
                        )
                    
                    messages.success(request, 'Case submitted successfully! Please choose a recovery plan.')
                    return redirect('payment', case_id=case.case_id)
                    
            except Exception as e:
                messages.error(request, f'Error submitting case: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ScamCaseForm(user=request.user)
    
    return render(request, 'cases/new.html', {
        'form': form,
    })

@login_required
def case_detail(request, case_id):
    case = get_object_or_404(ScamCase, case_id=case_id, user=request.user)
    status_updates = case.status_updates.all()
    evidence_files = case.evidence_files.all()
    recovery_transactions = case.recovery_transactions.all()
    deposits = case.deposits.all()
    
    context = {
        'case': case,
        'status_updates': status_updates,
        'evidence_files': evidence_files,
        'recovery_transactions': recovery_transactions,
        'deposits': deposits,
    }
    return render(request, 'cases/detail.html', context)

@login_required
def payment(request, case_id):
    case = get_object_or_404(ScamCase, case_id=case_id, user=request.user)
    plans = PaymentPlan.objects.filter(is_active=True)
    
    if request.method == 'POST':
        plan_id = request.POST.get('plan_id')
        
        try:
            plan = PaymentPlan.objects.get(id=plan_id, is_active=True)
            
            # Update case with selected plan
            case.payment_plan = plan
            case.status = 'verified'
            case.save()
            
            # Create status update
            CaseStatusUpdate.objects.create(
                case=case,
                old_status='submitted',
                new_status='verified',
                message=f'Payment plan selected: {plan.get_name_display()}. Deposit required: ${case.get_deposit_amount():.2f}',
                created_by=request.user
            )
            
            # Redirect directly to deposit page
            messages.success(request, f'Plan selected! Please make your deposit of ${case.get_deposit_amount():.2f} to start recovery.')
            return redirect('deposit', case_id=case.case_id)
            
        except PaymentPlan.DoesNotExist:
            messages.error(request, 'Invalid payment plan selected.')
    
    context = {
        'case': case,
        'plans': plans,
    }
    return render(request, 'payment/plans.html', context)

@login_required
def deposit(request, case_id):
    """Crypto deposit page for a specific case"""
    case = get_object_or_404(ScamCase, case_id=case_id, user=request.user)
    
    # Check if case already has a deposit
    existing_deposit = case.deposits.filter(status__in=['pending', 'under_review', 'completed']).first()
    if existing_deposit:
        messages.info(request, f'A deposit already exists for this case (Status: {existing_deposit.get_status_display()}).')
        return redirect('case_detail', case_id=case.case_id)
    
    # Check if case has a payment plan
    if not case.payment_plan:
        messages.error(request, 'Please select a payment plan first.')
        return redirect('payment', case_id=case.case_id)
    
    # Get active crypto wallets
    crypto_wallets = CryptoWallet.objects.filter(is_active=True)
    
    if request.method == 'POST':
        form = DepositForm(request.POST, request.FILES)
        if form.is_valid():
            deposit = form.save(commit=False)
            deposit.user = request.user
            deposit.case = case
            deposit.payment_method = 'crypto'
            deposit.amount = case.get_deposit_amount()  # Set the deposit amount
            deposit.status = 'pending'
            deposit.save()
            
            messages.success(request, 'Deposit submitted successfully! Please wait for confirmation. You will be notified once verified.')
            return redirect('case_detail', case_id=case.case_id)
    else:
        form = DepositForm()
    
    # Calculate deposit amount based on selected plan
    deposit_amount = case.get_deposit_amount()
    
    context = {
        'case': case,
        'form': form,
        'crypto_wallets': crypto_wallets,
        'deposit_amount': deposit_amount,
    }
    return render(request, 'payment/deposit.html', context)

@login_required
def deposit_success(request, deposit_id):
    """Deposit success page"""
    deposit = get_object_or_404(UserDeposit, deposit_id=deposit_id, user=request.user)
    
    context = {
        'deposit': deposit,
    }
    return render(request, 'payment/deposit_success.html', context)

@login_required
def withdraw(request):
    wallet = get_object_or_404(UserWallet, user=request.user)
    
    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            withdrawal = form.save(commit=False)
            withdrawal.user = request.user
            
            if withdrawal.amount > wallet.available_balance:
                messages.error(request, 'Insufficient balance for withdrawal.')
            elif withdrawal.amount < 10:  # Minimum withdrawal amount
                messages.error(request, 'Minimum withdrawal amount is $10.')
            else:
                withdrawal.save()
                
                # Update wallet (available balance decreases, pending balance increases)
                wallet.available_balance -= withdrawal.amount
                wallet.pending_balance += withdrawal.amount
                wallet.save()
                
                # Create notification
                Notification.objects.create(
                    user=request.user,
                    title='Withdrawal Request Submitted',
                    message=f'Your withdrawal request for ${withdrawal.amount} has been submitted and is under review.',
                    notification_type='withdrawal'
                )
                
                messages.success(request, 'Withdrawal request submitted successfully! It will be processed within 24-48 hours.')
                return redirect('withdrawal_history')
    else:
        form = WithdrawalForm()
    
    # Get withdrawal history
    withdrawal_history = WithdrawalRequest.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    context = {
        'form': form,
        'wallet': wallet,
        'withdrawal_history': withdrawal_history,
    }
    return render(request, 'payment/withdraw.html', context)

@login_required
def withdrawal_history(request):
    """View all withdrawal history with statistics"""
    withdrawals = WithdrawalRequest.objects.filter(user=request.user).order_by('-created_at')
    
    # Calculate statistics
    total_withdrawn = withdrawals.filter(status='completed').aggregate(
        total=models.Sum('amount')
    )['total'] or 0
    
    pending_count = withdrawals.filter(status='pending').count()
    processing_count = withdrawals.filter(status='processing').count()
    completed_count = withdrawals.filter(status='completed').count()
    rejected_count = withdrawals.filter(status='rejected').count()
    
    context = {
        'withdrawals': withdrawals,
        'total_withdrawn': total_withdrawn,
        'pending_count': pending_count,
        'processing_count': processing_count,
        'completed_count': completed_count,
        'rejected_count': rejected_count,
    }
    return render(request, 'payment/withdrawal_history.html', context)

# AJAX views
def get_scam_type_fields(request):
    scam_type = request.GET.get('scam_type')
    
    if scam_type == 'crypto':
        fields = {
            'blockchain': 'text',
            'victim_wallet': 'text', 
            'scammer_wallet': 'text',
            'transaction_hash': 'text',
            'exchange_used': 'text'
        }
    elif scam_type == 'banking':
        fields = {
            'bank_name': 'text',
            'account_debited': 'text',
            'beneficiary_details': 'textarea'
        }
    else:
        fields = {}
    
    return JsonResponse(fields)

@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(
        Notification, 
        id=notification_id, 
        user=request.user
    )
    notification.is_read = True
    notification.save()
    
    messages.success(request, 'Notification marked as read.')
    return redirect('dashboard')

@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    messages.success(request, 'All notifications marked as read.')
    return redirect('dashboard')

def password_reset_request(request):
    """Password reset request view"""
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Generate reset token
                token = str(uuid.uuid4())
                user.password_reset_token = token
                user.password_reset_token_created = timezone.now()
                user.save()
                
                # Create reset URL
                reset_url = request.build_absolute_uri(
                    f'/password-reset/{token}/'
                )
                
                # Send email
                try:
                    user.send_email_notification(
                        subject='Password Reset Request',
                        template_name='emails/password_reset.html',
                        context={
                            'user': user,
                            'reset_url': reset_url,
                            'expiry_hours': 24
                        }
                    )
                    
                    EmailLog.objects.create(
                        user=user,
                        email_type='password_reset',
                        subject='Password Reset Request',
                        recipient=email,
                        success=True
                    )
                    
                    messages.success(request, 'Password reset link sent to your email!')
                except Exception as e:
                    EmailLog.objects.create(
                        user=user,
                        email_type='password_reset',
                        subject='Password Reset Request',
                        recipient=email,
                        success=False,
                        error_message=str(e)
                    )
                    messages.error(request, 'Failed to send email. Please try again.')
            
            except User.DoesNotExist:
                # Don't reveal if email exists
                messages.success(request, 'If an account exists with this email, a reset link has been sent.')
            
            return redirect('login')
    else:
        form = CustomPasswordResetForm()
    
    return render(request, 'auth/password_reset_request.html', {'form': form})


def password_reset_confirm(request, token):
    """Password reset confirmation view"""
    try:
        user = User.objects.get(password_reset_token=token)
        
        # Check if token is expired (24 hours)
        if user.password_reset_token_created:
            expiry_time = user.password_reset_token_created + timedelta(hours=24)
            if timezone.now() > expiry_time:
                messages.error(request, 'Password reset link has expired. Please request a new one.')
                return redirect('password_reset_request')
        
        if request.method == 'POST':
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                
                # Clear reset token
                user.password_reset_token = None
                user.password_reset_token_created = None
                user.save()
                
                # Send confirmation email
                try:
                    user.send_email_notification(
                        subject='Password Reset Successful',
                        template_name='emails/password_reset_success.html',
                        context={'user': user}
                    )
                except:
                    pass
                
                messages.success(request, 'Password reset successful! You can now login with your new password.')
                return redirect('login')
        else:
            form = CustomSetPasswordForm(user)
        
        return render(request, 'auth/password_reset_confirm.html', {'form': form})
    
    except User.DoesNotExist:
        messages.error(request, 'Invalid password reset link.')
        return redirect('password_reset_request')


# ==================== CURRENCY HELPER VIEWS ====================
@login_required
def update_currency_preference(request):
    """AJAX view to update user's currency preference"""
    if request.method == 'POST':
        currency = request.POST.get('currency')
        
        if currency in dict(User.CURRENCY_CHOICES):
            request.user.preferred_currency = currency
            request.user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Currency preference updated',
                'currency': currency,
                'symbol': request.user.get_currency_symbol()
            })
        
        return JsonResponse({
            'success': False,
            'message': 'Invalid currency'
        }, status=400)
    
    return JsonResponse({'success': False}, status=400)


def convert_currency(amount, from_currency, to_currency):
    """
    Helper function to convert currency
    In production, integrate with a real currency API like:
    - exchangerate-api.com
    - fixer.io
    - currencylayer.com
    """
    # Placeholder conversion rates (replace with API calls)
    rates = {
        'USD': 1.0,
        'EUR': 0.85,
        'GBP': 0.73,
        'NGN': 1540.0,
        'CAD': 1.35,
        'AUD': 1.50,
    }
    
    if from_currency == to_currency:
        return amount
    
    # Convert to USD first, then to target currency
    usd_amount = amount / rates.get(from_currency, 1.0)
    return usd_amount * rates.get(to_currency, 1.0)

@login_required
def notifications_list(request):
    """View all notifications"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'unread_count': notifications.filter(is_read=False).count(),
    }
    return render(request, 'dashboard/notifications.html', context)

@login_required
def mark_notification_read(request, notification_id):
    """Mark a single notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, 'Notification marked as read.')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, 'All notifications marked as read.')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@login_required
def delete_account(request):
    """Allow users to delete their account"""
    if request.method == 'POST':
        password = request.POST.get('password')
        
        if request.user.check_password(password):
            # Check if user has any active cases or pending withdrawals
            active_cases = ScamCase.objects.filter(
                user=request.user
            ).exclude(status__in=['completed', 'rejected']).count()
            
            pending_withdrawals = WithdrawalRequest.objects.filter(
                user=request.user,
                status__in=['pending', 'processing']
            ).count()
            
            if active_cases > 0 or pending_withdrawals > 0:
                messages.error(
                    request, 
                    'Cannot delete account with active cases or pending withdrawals. '
                    'Please complete or cancel them first.'
                )
                return redirect('profile_settings')
            
            # Delete user account
            username = request.user.username
            request.user.delete()
            
            messages.success(request, f'Account {username} has been permanently deleted.')
            return redirect('home')
        else:
            messages.error(request, 'Incorrect password.')
            return redirect('profile_settings')
    
    return redirect('profile_settings')