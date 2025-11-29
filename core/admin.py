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