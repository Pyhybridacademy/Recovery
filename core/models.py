# core/models.py - ADD THESE TO YOUR EXISTING MODELS

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import uuid

def generate_case_id():
    return str(uuid.uuid4())[:8].upper()

def generate_deposit_id():
    return str(uuid.uuid4())[:12].upper()

def generate_withdrawal_id():
    return f"WD{str(uuid.uuid4())[:10].upper()}"


# Add this to your User model (UPDATE EXISTING)
# core/models.py - UPDATE THE User MODEL

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('user', 'User'),
        ('agent', 'Recovery Agent'),
        ('admin', 'Administrator'),
    )
    
    CURRENCY_CHOICES = (
        ('USD', 'US Dollar ($)'),
        ('EUR', 'Euro (€)'),
        ('GBP', 'British Pound (£)'),
        ('JPY', 'Japanese Yen (¥)'),
        ('CAD', 'Canadian Dollar (C$)'),
        ('AUD', 'Australian Dollar (A$)'),
        ('CHF', 'Swiss Franc (CHF)'),
        ('CNY', 'Chinese Yuan (¥)'),
        ('INR', 'Indian Rupee (₹)'),
        ('SGD', 'Singapore Dollar (S$)'),
        ('HKD', 'Hong Kong Dollar (HK$)'),
        ('NZD', 'New Zealand Dollar (NZ$)'),
        ('KRW', 'South Korean Won (₩)'),
        ('MXN', 'Mexican Peso ($)'),
        ('BRL', 'Brazilian Real (R$)'),
        ('RUB', 'Russian Ruble (₽)'),
        ('ZAR', 'South African Rand (R)'),
        ('TRY', 'Turkish Lira (₺)'),
        ('SEK', 'Swedish Krona (kr)'),
        ('NOK', 'Norwegian Krone (kr)'),
        ('DKK', 'Danish Krone (kr)'),
        ('PLN', 'Polish Złoty (zł)'),
        ('THB', 'Thai Baht (฿)'),
        ('IDR', 'Indonesian Rupiah (Rp)'),
        ('MYR', 'Malaysian Ringgit (RM)'),
        ('PHP', 'Philippine Peso (₱)'),
        ('VND', 'Vietnamese Đồng (₫)'),
        ('NGN', 'Nigerian Naira (₦)'),
        ('EGP', 'Egyptian Pound (E£)'),
        ('SAR', 'Saudi Riyal (﷼)'),
        ('AED', 'UAE Dirham (د.إ)'),
        ('QAR', 'Qatari Riyal (﷼)'),
        ('KWD', 'Kuwaiti Dinar (د.ك)'),
        ('BHD', 'Bahraini Dinar (.د.ب)'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='user')
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_phone_verified = models.BooleanField(default=False)
    is_kyc_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    preferred_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Password reset fields
    password_reset_token = models.CharField(max_length=100, blank=True, null=True)
    password_reset_token_created = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    def get_currency_symbol(self):
        """Return currency symbol for user's preferred currency"""
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
        return symbols.get(self.preferred_currency, '$')
            
    def send_email_notification(self, subject, template_name, context):
        """Helper method to send email notifications"""
        context['user'] = self
        html_message = render_to_string(template_name, context)
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.email],
            html_message=html_message,
            fail_silently=False,
        )

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    id_document = models.FileField(upload_to='kyc/', blank=True, null=True)
    id_number = models.CharField(max_length=50, blank=True, null=True)
    id_verified = models.BooleanField(default=False)
    id_verified_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Profile - {self.user.username}"

# ADD THIS NEW MODEL FOR KYC
class KYCVerification(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('resubmit', 'Resubmission Required'),
    )
    
    DOCUMENT_TYPES = (
        ('passport', 'Passport'),
        ('drivers_license', 'Driver\'s License'),
        ('national_id', 'National ID Card'),
        ('utility_bill', 'Utility Bill'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kyc_submissions')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document_number = models.CharField(max_length=100)
    document_front = models.ImageField(upload_to='kyc/documents/%Y/%m/')
    document_back = models.ImageField(upload_to='kyc/documents/%Y/%m/', blank=True, null=True)
    selfie = models.ImageField(upload_to='kyc/selfies/%Y/%m/')
    
    # Address verification
    proof_of_address = models.ImageField(upload_to='kyc/address/%Y/%m/', blank=True, null=True)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='kyc_reviews')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"KYC - {self.user.username} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        is_new = self._state.adding
        old_status = None
        
        if not is_new:
            try:
                old_status = KYCVerification.objects.get(pk=self.pk).status
            except KYCVerification.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Send email notifications on status change
        if old_status and old_status != self.status:
            if self.status == 'approved':
                self.user.is_kyc_verified = True
                self.user.save()
                
                # Send approval email
                self.user.send_email_notification(
                    subject='KYC Verification Approved',
                    template_name='emails/kyc_approved.html',
                    context={'kyc': self}
                )
                
                # Create notification
                Notification.objects.create(
                    user=self.user,
                    title='KYC Approved',
                    message='Your KYC verification has been approved. You now have full access to all features.',
                    notification_type='system'
                )
            
            elif self.status == 'rejected':
                self.user.is_kyc_verified = False
                self.user.save()
                
                # Send rejection email
                self.user.send_email_notification(
                    subject='KYC Verification Rejected',
                    template_name='emails/kyc_rejected.html',
                    context={'kyc': self}
                )
                
                # Create notification
                Notification.objects.create(
                    user=self.user,
                    title='KYC Rejected',
                    message=f'Your KYC verification was rejected. Reason: {self.rejection_reason}',
                    notification_type='system'
                )


# ADD THIS NEW MODEL FOR EMAIL LOGS
class EmailLog(models.Model):
    EMAIL_TYPES = (
        ('registration', 'Registration'),
        ('password_reset', 'Password Reset'),
        ('case_update', 'Case Update'),
        ('deposit_confirmation', 'Deposit Confirmation'),
        ('withdrawal_request', 'Withdrawal Request'),
        ('kyc_update', 'KYC Update'),
        ('recovery_notification', 'Recovery Notification'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_logs')
    email_type = models.CharField(max_length=30, choices=EMAIL_TYPES)
    subject = models.CharField(max_length=200)
    recipient = models.EmailField()
    sent_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.email_type} - {self.recipient}"


class PaymentPlan(models.Model):
    PLAN_TYPES = (
        ('starter', 'Starter Plan'),
        ('standard', 'Standard Plan'),
        ('premium', 'Premium Plan'),
    )
    
    name = models.CharField(max_length=50, choices=PLAN_TYPES)
    description = models.TextField()
    min_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    max_amount = models.DecimalField(max_digits=15, decimal_places=2)
    deposit_percentage = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    fixed_deposit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    features = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.get_name_display()

class ScamCase(models.Model):
    SCAM_TYPES = (
        ('crypto', 'Crypto Scam'),
        ('banking', 'Online Banking Scam'),
        ('investment', 'Investment Scam'),
        ('trading', 'Trading/Forex Scam'),
        ('payment', 'Payment Fraud'),
        ('wallet', 'Stolen Wallet'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('verified', 'Verified'),
        ('investigation', 'Investigation Started'),
        ('tracing', 'Wallet/Account Tracing'),
        ('evidence', 'Evidence Gathering'),
        ('recovery', 'Recovery in Progress'),
        ('secured', 'Funds Secured'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    )
    
    case_id = models.CharField(max_length=20, unique=True, default=generate_case_id)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cases')
    scam_type = models.CharField(max_length=20, choices=SCAM_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    amount_lost = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    incident_date = models.DateField()
    
    # Crypto-specific fields
    blockchain = models.CharField(max_length=50, blank=True, null=True)
    victim_wallet = models.CharField(max_length=255, blank=True, null=True)
    scammer_wallet = models.CharField(max_length=255, blank=True, null=True)
    transaction_hash = models.CharField(max_length=255, blank=True, null=True)
    exchange_used = models.CharField(max_length=100, blank=True, null=True)
    
    # Bank scam fields
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_debited = models.CharField(max_length=100, blank=True, null=True)
    beneficiary_details = models.TextField(blank=True, null=True)
    
    # General suspect info
    suspect_email = models.EmailField(blank=True, null=True)
    suspect_phone = models.CharField(max_length=20, blank=True, null=True)
    suspect_website = models.URLField(blank=True, null=True)
    
    # Case management
    payment_plan = models.ForeignKey(PaymentPlan, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    assigned_agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_cases')
    risk_score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Case {self.case_id} - {self.user.username}"
    
    def get_deposit_amount(self):
        """Calculate deposit amount based on selected plan"""
        if self.payment_plan:
            if self.payment_plan.fixed_deposit:
                return self.payment_plan.fixed_deposit
            else:
                return (self.amount_lost * self.payment_plan.deposit_percentage) / 100
        return 0

    def update_wallet_on_recovery(self):
        """Update user wallet when funds are recovered"""
        if self.status == 'secured':
            total_recovered = self.recovery_transactions.aggregate(
                total=models.Sum('amount_recovered')
            )['total'] or 0
            
            wallet, created = UserWallet.objects.get_or_create(user=self.user)
            wallet.available_balance += total_recovered
            wallet.total_recovered += total_recovered
            wallet.save()

    def create_notification(self, title, message, notification_type='case_update'):
        """Helper method to create notifications"""
        Notification.objects.create(
            user=self.user,
            title=title,
            message=message,
            notification_type=notification_type,
            related_case=self
        )

    def get_total_recovered(self):
        """Calculate total recovered amount for this case"""
        return self.recovery_transactions.aggregate(
            total=models.Sum('amount_recovered')
        )['total'] or 0
    
    def get_total_deposits(self):
        """Calculate total deposits for this case"""
        return self.deposits.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
    
    def get_progress_percentage(self):
        """Calculate progress percentage based on status"""
        status_order = {
            'submitted': 10,
            'verified': 20,
            'investigation': 40,
            'tracing': 50,
            'evidence': 60,
            'recovery': 75,
            'secured': 90,
            'completed': 100,
            'rejected': 100
        }
        return status_order.get(self.status, 10)
    
    def get_status_order(self):
        """Get numerical order of current status"""
        status_order = {
            'submitted': 1,
            'verified': 2,
            'investigation': 3,
            'tracing': 4,
            'evidence': 5,
            'recovery': 6,
            'secured': 7,
            'completed': 8,
            'rejected': 9
        }
        return status_order.get(self.status, 1)
    

    def get_scam_type_icon(self):
        """Return appropriate icon for scam type"""
        icons = {
            'crypto': 'bitcoin',
            'banking': 'university',
            'investment': 'chart-line',
            'trading': 'chart-bar',
            'payment': 'credit-card',
            'wallet': 'wallet',
            'other': 'exclamation-triangle'
        }
        return icons.get(self.scam_type, 'folder-open')
    
    def get_progress_percentage(self):
        """Calculate progress percentage based on status"""
        status_progress = {
            'submitted': 10,
            'verified': 20,
            'investigation': 40,
            'tracing': 50,
            'evidence': 60,
            'recovery': 75,
            'secured': 90,
            'completed': 100,
            'rejected': 100
        }
        return status_progress.get(self.status, 10)
    
    def get_total_recovered(self):
        """Calculate total recovered amount for this case"""
        return self.recovery_transactions.aggregate(
            total=models.Sum('amount_recovered')
        )['total'] or 0


class EvidenceFile(models.Model):
    case = models.ForeignKey(ScamCase, on_delete=models.CASCADE, related_name='evidence_files')
    file = models.FileField(upload_to='evidence/%Y/%m/%d/')
    file_type = models.CharField(max_length=50)  # screenshot, receipt, etc.
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Evidence for {self.case.case_id}"

class CaseStatusUpdate(models.Model):
    case = models.ForeignKey(ScamCase, on_delete=models.CASCADE, related_name='status_updates')
    old_status = models.CharField(max_length=20, choices=ScamCase.STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=ScamCase.STATUS_CHOICES)
    message = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        """Override save to create notifications for status changes"""
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        if is_new and self.old_status != self.new_status:
            # Create notification for user
            Notification.objects.create(
                user=self.case.user,
                title='Case Status Updated',
                message=f'Your case {self.case.case_id} status changed from {self.get_old_status_display()} to {self.get_new_status_display()}',
                notification_type='case_update',
                related_case=self.case
            )

# Update UserDeposit model to handle crypto-specific fields better
class UserDeposit(models.Model):
    PAYMENT_METHODS = (
        ('crypto', 'Cryptocurrency'),
        # Remove other methods since we're crypto-only
    )
    
    CRYPTO_CHOICES = (
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'), 
        ('USDT', 'Tether (USDT)'),
        ('USDC', 'USD Coin (USDC)'),
    )
    
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('under_review', 'Under Review'),
    )
    
    deposit_id = models.CharField(max_length=20, unique=True, default=generate_deposit_id)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deposits')
    case = models.ForeignKey(ScamCase, on_delete=models.CASCADE, related_name='deposits')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='crypto')
    
    # Crypto payment details
    crypto_currency = models.CharField(max_length=10, null=True, choices=CRYPTO_CHOICES)
    crypto_amount = models.DecimalField(max_digits=15, decimal_places=8, null=True, blank=True)
    transaction_hash = models.CharField(max_length=255, blank=True, null=True)
    receipt_proof = models.FileField(upload_to='deposit_receipts/%Y/%m/%d/', blank=True, null=True)
    
    status = models.CharField(max_length=15, choices=PAYMENT_STATUS, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    user_currency = models.CharField(max_length=3, default='USD')
    amount_in_user_currency = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        is_new = self._state.adding
        
        # Store user's currency and calculate amount in USD
        if is_new:
            self.user_currency = self.user.preferred_currency
            # In production, fetch real exchange rates from an API
            # For now, we'll store the same amount
            self.amount_in_user_currency = self.amount
            self.exchange_rate = 1.0
        
        old_status = None
        if not is_new:
            try:
                old_status = UserDeposit.objects.get(pk=self.pk).status
            except UserDeposit.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Send emails on status changes
        if old_status and old_status != self.status:
            if self.status == 'completed':
                self.completed_at = timezone.now()
                self.save(update_fields=['completed_at'])
                
                # Send confirmation email
                self.user.send_email_notification(
                    subject='Deposit Confirmed',
                    template_name='emails/deposit_confirmed.html',
                    context={'deposit': self}
                )
                
                # Update case status
                self.case.status = 'investigation'
                self.case.save()
                
                CaseStatusUpdate.objects.create(
                    case=self.case,
                    old_status='verified',
                    new_status='investigation',
                    message='Deposit confirmed. Investigation has started.',
                    created_by=self.user
                )
            
            elif self.status == 'failed':
                self.user.send_email_notification(
                    subject='Deposit Failed',
                    template_name='emails/deposit_failed.html',
                    context={'deposit': self}
                )

    
    def __str__(self):
        return f"Deposit {self.deposit_id} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        """Override save to create notifications"""
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        if is_new:
            # Create notification for user
            Notification.objects.create(
                user=self.user,
                title='Deposit Initiated',
                message=f'Deposit of ${self.amount} for case {self.case.case_id} has been initiated.',
                notification_type='payment',
                related_case=self.case
            )

class RecoveryTransaction(models.Model):
    case = models.ForeignKey(ScamCase, on_delete=models.CASCADE, related_name='recovery_transactions')
    amount_recovered = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    recovery_method = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    recovery_date = models.DateField()
    transaction_proof = models.FileField(upload_to='recovery_proofs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Recovery ${self.amount_recovered} - {self.case.case_id}"
    
    def save(self, *args, **kwargs):
        """Override save to update wallet and create notification"""
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        if is_new:
            # Update user wallet
            wallet, created = UserWallet.objects.get_or_create(user=self.case.user)
            wallet.available_balance += self.amount_recovered
            wallet.total_recovered += self.amount_recovered
            wallet.save()
            
            # Create notification
            Notification.objects.create(
                user=self.case.user,
                title='Funds Recovered!',
                message=f'${self.amount_recovered} has been recovered for case {self.case.case_id}',
                notification_type='payment',
                related_case=self.case
            )

class UserWallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    available_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    pending_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_recovered = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Wallet - {self.user.username}"
    
    def get_total_balance(self):
        """Get total balance (available + pending)"""
        return self.available_balance + self.pending_balance

    def can_withdraw(self, amount):
        """Check if user can withdraw specified amount"""
        return self.available_balance >= amount
    
    def get_currency_symbol(self):
        """Get currency symbol from user's preferred currency"""
        return self.user.get_currency_symbol()

class WithdrawalRequest(models.Model):
    WITHDRAWAL_METHODS = (
        ('bank', 'Bank Transfer'),
        ('crypto', 'Cryptocurrency'),
        ('paypal', 'PayPal'),
        ('cashapp', 'CashApp'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    )
    
    request_id = models.CharField(max_length=20, unique=True, default=generate_withdrawal_id)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    method = models.CharField(max_length=10, choices=WITHDRAWAL_METHODS)
    
    # Bank details
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=100, blank=True, null=True)
    routing_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Crypto details
    crypto_currency = models.CharField(max_length=10, blank=True, null=True)
    crypto_wallet = models.CharField(max_length=255, blank=True, null=True)
    
    # Other methods
    paypal_email = models.EmailField(blank=True, null=True)
    cashapp_id = models.CharField(max_length=100, blank=True, null=True)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    user_currency = models.CharField(max_length=3, default='USD')
    amount_in_user_currency = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        is_new = self._state.adding
        old_status = None
        
        if is_new:
            self.user_currency = self.user.preferred_currency
            self.amount_in_user_currency = self.amount
            self.exchange_rate = 1.0
        else:
            try:
                old_status = WithdrawalRequest.objects.get(pk=self.pk).status
            except WithdrawalRequest.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Send email notifications on status changes
        if old_status and old_status != self.status:
            if self.status == 'approved':
                self.user.send_email_notification(
                    subject='Withdrawal Request Approved',
                    template_name='emails/withdrawal_approved.html',
                    context={'withdrawal': self}
                )
            
            elif self.status == 'completed':
                self.processed_at = timezone.now()
                self.save(update_fields=['processed_at'])
                
                # Update wallet
                wallet = self.user.wallet
                wallet.pending_balance -= self.amount
                wallet.save()
                
                self.user.send_email_notification(
                    subject='Withdrawal Completed',
                    template_name='emails/withdrawal_completed.html',
                    context={'withdrawal': self}
                )
            
            elif self.status == 'rejected':
                # Refund to available balance
                wallet = self.user.wallet
                wallet.available_balance += self.amount
                wallet.pending_balance -= self.amount
                wallet.save()
                
                self.user.send_email_notification(
                    subject='Withdrawal Request Rejected',
                    template_name='emails/withdrawal_rejected.html',
                    context={'withdrawal': self}
                )
    
    def __str__(self):
        return f"Withdrawal {self.request_id} - {self.user.username}"

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('case_update', 'Case Update'),
        ('payment', 'Payment'),
        ('withdrawal', 'Withdrawal'),
        ('system', 'System'),
        ('message', 'Message'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_case = models.ForeignKey(ScamCase, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} - {self.user.username}"

class AdminMessage(models.Model):
    case = models.ForeignKey(ScamCase, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message {self.id} - {self.case.case_id}"
    
    def save(self, *args, **kwargs):
        """Override save to create notifications for new messages"""
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        if is_new:
            Notification.objects.create(
                user=self.recipient,
                title='New Message from Admin',
                message=f'You have a new message regarding case {self.case.case_id}',
                notification_type='message',
                related_case=self.case
            )


# core/models.py - Add these new models and update existing ones

class CryptoWallet(models.Model):
    CRYPTO_CHOICES = (
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT', 'Tether (USDT)'),
        ('USDC', 'USD Coin (USDC)'),
    )
    
    currency = models.CharField(max_length=10, choices=CRYPTO_CHOICES, unique=True)
    wallet_address = models.CharField(max_length=255)
    qr_code = models.ImageField(upload_to='crypto_qr_codes/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_currency_display()} - {self.wallet_address[:20]}..."

