# core/admin.py - COMPLETE ADMIN CONFIGURATION

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import *


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'user_type', 'preferred_currency', 'is_kyc_verified', 'is_active', 'date_joined']
    list_filter = ['user_type', 'is_kyc_verified', 'is_active', 'preferred_currency', 'date_joined']
    search_fields = ['username', 'email', 'phone']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone', 'is_phone_verified', 'is_kyc_verified', 
                      'two_factor_enabled', 'preferred_currency')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'email', 'phone', 'preferred_currency')
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'city', 'country', 'id_verified', 'id_verified_at']
    list_filter = ['id_verified', 'country']
    search_fields = ['user__username', 'user__email', 'city', 'country']
    readonly_fields = ['id_verified_at']


@admin.register(KYCVerification)
class KYCVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'document_type', 'status', 'submitted_at', 'reviewed_by', 'reviewed_at']
    list_filter = ['status', 'document_type', 'submitted_at']
    search_fields = ['user__username', 'user__email', 'document_number']
    readonly_fields = ['submitted_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'document_type', 'document_number')
        }),
        ('Documents', {
            'fields': ('document_front', 'document_back', 'selfie', 'proof_of_address')
        }),
        ('Review', {
            'fields': ('status', 'rejection_reason', 'reviewed_by', 'reviewed_at')
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_kyc', 'reject_kyc']
    
    def approve_kyc(self, request, queryset):
        for kyc in queryset:
            kyc.status = 'approved'
            kyc.reviewed_by = request.user
            kyc.reviewed_at = timezone.now()
            kyc.save()
        self.message_user(request, f'{queryset.count()} KYC verification(s) approved.')
    approve_kyc.short_description = 'Approve selected KYC verifications'
    
    def reject_kyc(self, request, queryset):
        for kyc in queryset:
            if not kyc.rejection_reason:
                kyc.rejection_reason = 'Documents unclear or invalid. Please resubmit.'
            kyc.status = 'rejected'
            kyc.reviewed_by = request.user
            kyc.reviewed_at = timezone.now()
            kyc.save()
        self.message_user(request, f'{queryset.count()} KYC verification(s) rejected.')
    reject_kyc.short_description = 'Reject selected KYC verifications'


@admin.register(ScamCase)
class ScamCaseAdmin(admin.ModelAdmin):
    list_display = ['case_id', 'user', 'scam_type', 'amount_lost', 'currency', 'status', 'assigned_agent', 'created_at']
    list_filter = ['status', 'scam_type', 'currency', 'created_at']
    search_fields = ['case_id', 'user__username', 'user__email', 'title', 'description']
    readonly_fields = ['case_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Case Information', {
            'fields': ('case_id', 'user', 'scam_type', 'title', 'description')
        }),
        ('Financial Details', {
            'fields': ('amount_lost', 'currency', 'payment_plan')
        }),
        ('Incident Details', {
            'fields': ('incident_date', 'blockchain', 'victim_wallet', 'scammer_wallet', 
                      'transaction_hash', 'exchange_used', 'bank_name', 'account_debited',
                      'beneficiary_details')
        }),
        ('Suspect Information', {
            'fields': ('suspect_email', 'suspect_phone', 'suspect_website')
        }),
        ('Case Management', {
            'fields': ('status', 'assigned_agent', 'risk_score')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'submitted_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_investigation', 'mark_as_recovery', 'mark_as_completed']
    
    def mark_as_investigation(self, request, queryset):
        queryset.update(status='investigation')
        self.message_user(request, f'{queryset.count()} case(s) marked as Investigation.')
    mark_as_investigation.short_description = 'Mark as Investigation Started'
    
    def mark_as_recovery(self, request, queryset):
        queryset.update(status='recovery')
        self.message_user(request, f'{queryset.count()} case(s) marked as Recovery in Progress.')
    mark_as_recovery.short_description = 'Mark as Recovery in Progress'
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed', completed_at=timezone.now())
        self.message_user(request, f'{queryset.count()} case(s) marked as Completed.')
    mark_as_completed.short_description = 'Mark as Completed'


@admin.register(UserDeposit)
class UserDepositAdmin(admin.ModelAdmin):
    list_display = ['deposit_id', 'user', 'case', 'amount', 'crypto_currency', 'status', 'created_at']
    list_filter = ['status', 'crypto_currency', 'payment_method', 'created_at']
    search_fields = ['deposit_id', 'user__username', 'case__case_id', 'transaction_hash']
    readonly_fields = ['deposit_id', 'created_at', 'completed_at']
    
    fieldsets = (
        ('Deposit Information', {
            'fields': ('deposit_id', 'user', 'case', 'amount', 'payment_method')
        }),
        ('Crypto Details', {
            'fields': ('crypto_currency', 'crypto_amount', 'transaction_hash', 'receipt_proof')
        }),
        ('Status', {
            'fields': ('status', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_deposit', 'reject_deposit']
    
    def approve_deposit(self, request, queryset):
        for deposit in queryset.filter(status='pending'):
            deposit.status = 'completed'
            deposit.completed_at = timezone.now()
            deposit.save()
        self.message_user(request, f'{queryset.count()} deposit(s) approved.')
    approve_deposit.short_description = 'Approve selected deposits'
    
    def reject_deposit(self, request, queryset):
        queryset.filter(status='pending').update(status='failed')
        self.message_user(request, f'{queryset.count()} deposit(s) rejected.')
    reject_deposit.short_description = 'Reject selected deposits'


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ['request_id', 'user', 'amount', 'method', 'status', 'created_at']
    list_filter = ['status', 'method', 'created_at']
    search_fields = ['request_id', 'user__username', 'user__email']
    readonly_fields = ['request_id', 'created_at', 'processed_at']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('request_id', 'user', 'amount', 'method')
        }),
        ('Payment Details', {
            'fields': ('bank_name', 'account_number', 'routing_number', 
                      'crypto_currency', 'crypto_wallet', 'paypal_email', 'cashapp_id')
        }),
        ('Status', {
            'fields': ('status', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'processed_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_withdrawal', 'complete_withdrawal', 'reject_withdrawal']
    
    def approve_withdrawal(self, request, queryset):
        queryset.filter(status='pending').update(status='approved')
        self.message_user(request, f'{queryset.count()} withdrawal(s) approved.')
    approve_withdrawal.short_description = 'Approve selected withdrawals'
    
    def complete_withdrawal(self, request, queryset):
        for withdrawal in queryset.filter(status__in=['pending', 'approved', 'processing']):
            withdrawal.status = 'completed'
            withdrawal.processed_at = timezone.now()
            withdrawal.save()
        self.message_user(request, f'{queryset.count()} withdrawal(s) marked as completed.')
    complete_withdrawal.short_description = 'Mark as Completed'
    
    def reject_withdrawal(self, request, queryset):
        for withdrawal in queryset.filter(status='pending'):
            withdrawal.status = 'rejected'
            withdrawal.processed_at = timezone.now()
            withdrawal.save()
        self.message_user(request, f'{queryset.count()} withdrawal(s) rejected.')
    reject_withdrawal.short_description = 'Reject selected withdrawals'


@admin.register(RecoveryTransaction)
class RecoveryTransactionAdmin(admin.ModelAdmin):
    list_display = ['case', 'amount_recovered', 'currency', 'recovery_method', 'recovery_date', 'created_at']
    list_filter = ['currency', 'recovery_date', 'created_at']
    search_fields = ['case__case_id', 'case__user__username', 'recovery_method']
    readonly_fields = ['created_at']


@admin.register(UserWallet)
class UserWalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'available_balance', 'pending_balance', 'total_recovered', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['updated_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at']


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_type', 'recipient', 'success', 'sent_at']
    list_filter = ['email_type', 'success', 'sent_at']
    search_fields = ['user__username', 'recipient', 'subject']
    readonly_fields = ['sent_at']


@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'min_amount', 'max_amount', 'deposit_percentage', 'fixed_deposit', 'is_active']
    list_filter = ['is_active', 'name']


@admin.register(CryptoWallet)
class CryptoWalletAdmin(admin.ModelAdmin):
    list_display = ['currency', 'wallet_address_short', 'is_active', 'created_at']
    list_filter = ['currency', 'is_active']
    
    def wallet_address_short(self, obj):
        return f"{obj.wallet_address[:20]}..."
    wallet_address_short.short_description = 'Wallet Address'


@admin.register(EvidenceFile)
class EvidenceFileAdmin(admin.ModelAdmin):
    list_display = ['case', 'file_type', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['case__case_id', 'description']


@admin.register(CaseStatusUpdate)
class CaseStatusUpdateAdmin(admin.ModelAdmin):
    list_display = ['case', 'old_status', 'new_status', 'created_by', 'created_at']
    list_filter = ['old_status', 'new_status', 'created_at']
    search_fields = ['case__case_id', 'message']
    readonly_fields = ['created_at']


@admin.register(AdminMessage)
class AdminMessageAdmin(admin.ModelAdmin):
    list_display = ['case', 'sender', 'recipient', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['case__case_id', 'sender__username', 'recipient__username', 'message']
    readonly_fields = ['created_at']



models.py

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
        ('NGN', 'Nigerian Naira (₦)'),
        ('CAD', 'Canadian Dollar (C$)'),
        ('AUD', 'Australian Dollar (A$)'),
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
            'NGN': '₦',
            'CAD': 'C$',
            'AUD': 'A$',
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



forms.py

# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model
from .models import *

User = get_user_model()

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
        'placeholder': 'Enter your email address'
    }))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
        'placeholder': 'Enter your phone number (optional)'
    }))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update widget attributes for all fields
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
            'placeholder': 'Enter your password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
            'placeholder': 'Confirm your password'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
        return user

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['date_of_birth', 'address', 'city', 'country', 'id_document']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'address': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'country': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'id_document': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
        }

class ScamCaseForm(forms.ModelForm):
    evidence_files = MultipleFileField(
        required=False,
        help_text='Upload screenshots, transaction proofs, or any relevant evidence (multiple files allowed)',
        widget=MultipleFileInput(attrs={
            'id': 'id_evidence_files',
            'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx,.txt',
            'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
        })
    )
    
    class Meta:
        model = ScamCase
        fields = [
            'scam_type', 'title', 'description', 'amount_lost', 'currency', 
            'incident_date', 'blockchain', 'victim_wallet', 'scammer_wallet',
            'transaction_hash', 'exchange_used', 'bank_name', 'account_debited',
            'beneficiary_details', 'suspect_email', 'suspect_phone', 'suspect_website'
        ]
        widgets = {
            'scam_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'title': forms.TextInput(attrs={
                'placeholder': 'Brief description of what happened',
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'incident_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'description': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Describe the incident in detail...',
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'amount_lost': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'currency': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'blockchain': forms.TextInput(attrs={
                'placeholder': 'e.g., Bitcoin, Ethereum, BSC',
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'victim_wallet': forms.TextInput(attrs={
                'placeholder': 'Your wallet address',
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'scammer_wallet': forms.TextInput(attrs={
                'placeholder': 'Scammer\'s wallet address',
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'transaction_hash': forms.TextInput(attrs={
                'placeholder': 'Transaction hash or ID',
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'exchange_used': forms.TextInput(attrs={
                'placeholder': 'e.g., Binance, Coinbase, Kraken',
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'bank_name': forms.TextInput(attrs={
                'placeholder': 'Name of your bank',
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'account_debited': forms.TextInput(attrs={
                'placeholder': 'Last 4 digits of account',
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'beneficiary_details': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Beneficiary name, account number, bank details',
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'suspect_email': forms.EmailInput(attrs={
                'placeholder': 'suspect@example.com',
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'suspect_phone': forms.TextInput(attrs={
                'placeholder': '+1 (555) 000-0000',
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'suspect_website': forms.URLInput(attrs={
                'placeholder': 'https://example.com or social media profile URL',
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make scam-specific fields not required initially
        scam_specific_fields = [
            'blockchain', 'victim_wallet', 'scammer_wallet', 'transaction_hash',
            'exchange_used', 'bank_name', 'account_debited', 'beneficiary_details',
            'suspect_email', 'suspect_phone', 'suspect_website'
        ]
        for field in scam_specific_fields:
            self.fields[field].required = False

class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = WithdrawalRequest
        fields = ['amount', 'method', 'bank_name', 'account_number', 'routing_number', 
                 'crypto_currency', 'crypto_wallet', 'paypal_email', 'cashapp_id']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'min': 1,
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'method': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'bank_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'account_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'routing_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'crypto_currency': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'crypto_wallet': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'paypal_email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'cashapp_id': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields not required initially, they'll be validated based on method
        for field in self.fields:
            self.fields[field].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get('method')
        amount = cleaned_data.get('amount')
        
        if not amount or amount <= 0:
            raise forms.ValidationError('Please enter a valid withdrawal amount.')
        
        # Validate method-specific fields
        if method == 'bank':
            if not cleaned_data.get('bank_name') or not cleaned_data.get('account_number'):
                raise forms.ValidationError('Bank name and account number are required for bank transfers.')
        elif method == 'crypto':
            if not cleaned_data.get('crypto_currency') or not cleaned_data.get('crypto_wallet'):
                raise forms.ValidationError('Cryptocurrency and wallet address are required for crypto withdrawals.')
        elif method == 'paypal':
            if not cleaned_data.get('paypal_email'):
                raise forms.ValidationError('PayPal email is required for PayPal withdrawals.')
        elif method == 'cashapp':
            if not cleaned_data.get('cashapp_id'):
                raise forms.ValidationError('CashApp ID is required for CashApp withdrawals.')
        
        return cleaned_data

class DepositForm(forms.ModelForm):
    class Meta:
        model = UserDeposit
        fields = ['crypto_currency', 'transaction_hash', 'receipt_proof']
        widgets = {
            'crypto_currency': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'transaction_hash': forms.TextInput(attrs={
                'placeholder': 'Enter your transaction hash from blockchain explorer',
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'receipt_proof': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
                'accept': 'image/*,.pdf'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['receipt_proof'].required = True
        self.fields['receipt_proof'].help_text = 'Upload screenshot of your transaction confirmation'

class KYCVerificationForm(forms.ModelForm):
    """Form for users to submit KYC documents"""
    
    class Meta:
        model = KYCVerification
        fields = [
            'document_type', 
            'document_number', 
            'document_front', 
            'document_back',
            'selfie',
            'proof_of_address'
        ]
        widgets = {
            'document_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'document_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
                'placeholder': 'Enter your document number'
            }),
            'document_front': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
                'accept': 'image/*'
            }),
            'document_back': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
                'accept': 'image/*'
            }),
            'selfie': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
                'accept': 'image/*'
            }),
            'proof_of_address': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
                'accept': 'image/*,.pdf'
            }),
        }
        help_texts = {
            'document_front': 'Upload clear photo of the front of your ID',
            'document_back': 'Upload clear photo of the back of your ID (if applicable)',
            'selfie': 'Upload a clear selfie holding your ID',
            'proof_of_address': 'Upload utility bill or bank statement (not older than 3 months)',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        document_type = cleaned_data.get('document_type')
        document_back = cleaned_data.get('document_back')
        
        # Require back image for certain document types
        if document_type in ['drivers_license', 'national_id'] and not document_back:
            raise forms.ValidationError(
                f'Back image is required for {self.get_document_type_display()}'
            )
        
        return cleaned_data

class EnhancedUserUpdateForm(forms.ModelForm):
    """Enhanced user update form with currency preference"""
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'preferred_currency']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
                'placeholder': '+1234567890'
            }),
            'preferred_currency': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
        }

class EnhancedProfileUpdateForm(forms.ModelForm):
    """Enhanced profile update form"""
    
    class Meta:
        model = UserProfile
        fields = ['date_of_birth', 'address', 'city', 'country']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'address': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
                'placeholder': 'Enter your full address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
            'country': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
            }),
        }

class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form with better styling"""
    
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        })
    )

class CustomSetPasswordForm(SetPasswordForm):
    """Custom set password form with better styling"""
    
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
            'placeholder': 'Enter new password',
            'autocomplete': 'new-password'
        }),
        strip=False,
    )
    new_password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
            'placeholder': 'Confirm new password',
            'autocomplete': 'new-password'
        }),
        strip=False,
    )

class ChangePasswordForm(forms.Form):
    """Form for users to change their password from profile settings"""
    
    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
            'placeholder': 'Enter current password'
        })
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
            'placeholder': 'Enter new password'
        }),
        help_text='Password must be at least 8 characters long'
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
            'placeholder': 'Confirm new password'
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('Current password is incorrect.')
        return old_password
    
    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError('The two password fields must match.')
            
            if len(new_password1) < 8:
                raise forms.ValidationError('Password must be at least 8 characters long.')
        
        return cleaned_data
    
    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user

class TwoFactorToggleForm(forms.Form):
    """Form to enable/disable 2FA"""
    
    enable_2fa = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-cyan focus:ring-cyan border-coolGray rounded'
        })
    )

class NotificationPreferencesForm(forms.Form):
    """Form for users to manage notification preferences"""
    
    email_case_updates = forms.BooleanField(
        required=False,
        label='Case Status Updates',
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-cyan focus:ring-cyan border-coolGray rounded'
        })
    )
    email_payment_updates = forms.BooleanField(
        required=False,
        label='Payment Notifications',
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-cyan focus:ring-cyan border-coolGray rounded'
        })
    )
    email_withdrawal_updates = forms.BooleanField(
        required=False,
        label='Withdrawal Updates',
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-cyan focus:ring-cyan border-coolGray rounded'
        })
    )
    email_marketing = forms.BooleanField(
        required=False,
        label='Marketing & Promotions',
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-cyan focus:ring-cyan border-coolGray rounded'
        })
    )

urls.py

# core/urls.py - REPLACE YOUR EXISTING urls.py WITH THIS

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Static pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('faq/', views.faq, name='faq'),
    path('contact/', views.contact, name='contact'),
    
    # Auth
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Password Reset
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('settings/', views.profile_settings, name='profile_settings'),  # New comprehensive settings
    
    # KYC
    path('kyc/', views.kyc_verification, name='kyc_verification'),
    
    # Withdrawals
    path('withdraw/', views.withdraw, name='withdraw'),
    path('withdrawal/history/', views.withdrawal_history, name='withdrawal_history'),
    
    # Cases
    path('cases/', views.case_list, name='cases'),
    path('cases/new/', views.new_case, name='new_case'),
    path('cases/<str:case_id>/', views.case_detail, name='case_detail'),
    
    # Payments
    path('payment/<str:case_id>/', views.payment, name='payment'),
    path('deposit/<str:case_id>/', views.deposit, name='deposit'),
    path('deposit/success/<str:deposit_id>/', views.deposit_success, name='deposit_success'),
    
    # Notifications
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    
    # AJAX/API endpoints
    path('ajax/get-scam-type-fields/', views.get_scam_type_fields, name='get_scam_type_fields'),
    path('ajax/update-currency/', views.update_currency_preference, name='update_currency_preference'),
    
    # Account Management
    path('delete-account/', views.delete_account, name='delete_account'),
]


views.py

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

@login_required
def new_case(request):
    if request.method == 'POST':
        form = ScamCaseForm(request.POST, request.FILES)
        if form.is_valid():
            case = form.save(commit=False)
            case.user = request.user
            case.save()
            
            # Handle file uploads
            files = request.FILES.getlist('evidence_files')
            for file in files:
                EvidenceFile.objects.create(
                    case=case,
                    file=file,
                    file_type=file.content_type
                )
            
            messages.success(request, 'Case submitted successfully! Please choose a recovery plan.')
            return redirect('payment', case_id=case.case_id)
    else:
        form = ScamCaseForm()
    
    return render(request, 'cases/new.html', {'form': form})

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


utils.py

# core/utils.py - CREATE THIS NEW FILE

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
    
    # Fallback rates (update these periodically or cache them)
    fallback_rates = {
        'USD': Decimal('1.0'),
        'EUR': Decimal('0.85'),
        'GBP': Decimal('0.73'),
        'NGN': Decimal('1540.0'),
        'CAD': Decimal('1.35'),
        'AUD': Decimal('1.50'),
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
        'NGN': '₦',
        'CAD': 'C$',
        'AUD': 'A$',
    }
    
    symbol = symbols.get(currency_code, '$')
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
    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
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
    
    return {
        'total_cases': cases.count(),
        'active_cases': cases.exclude(status__in=['completed', 'rejected']).count(),
        'completed_cases': cases.filter(status='completed').count(),
        'rejected_cases': cases.filter(status='rejected').count(),
        'total_lost': cases.aggregate(total=Sum('amount_lost'))['total'] or Decimal('0'),
        'total_recovered': RecoveryTransaction.objects.filter(
            case__user=user
        ).aggregate(total=Sum('amount_recovered'))['total'] or Decimal('0'),
        'recovery_rate': 0,  # Calculate based on recovered vs lost
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
            message=f'New case {case.case_id} submitted by {case.user.username}. Amount: ${case.amount_lost}',
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


# Context processor for currency
def currency_context(request):
    """
    Add currency information to all templates
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




i want us to modify the registeration page to include currency so that after registration the chosen currency will display on the dashboard, 