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
# core/forms.py - UPDATE THE UserRegistrationForm

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
        'placeholder': 'Enter your email address'
    }))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
        'placeholder': 'Enter your phone number (optional)'
    }))
    preferred_currency = forms.ChoiceField(
        choices=User.CURRENCY_CHOICES,
        initial='USD',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition'
        }),
        help_text="Select your preferred currency for all transactions"
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'preferred_currency', 'password1', 'password2']
    
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
        user.preferred_currency = self.cleaned_data['preferred_currency']
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

# core/forms.py - COMPLETE ScamCaseForm

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
            'scam_type', 'title', 'description', 'amount_lost', 
            'incident_date', 'blockchain', 'victim_wallet', 'scammer_wallet',
            'transaction_hash', 'exchange_used', 'bank_name', 'account_debited',
            'beneficiary_details', 'suspect_email', 'suspect_phone', 'suspect_website'
        ]  # Remove 'currency' from fields
        
        widgets = {
            'scam_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
                'required': 'true'
            }),
            'title': forms.TextInput(attrs={
                'placeholder': 'Brief description of what happened',
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
                'required': 'true'
            }),
            'incident_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
                'required': 'true'
            }),
            'description': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Describe the incident in detail...',
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
                'required': 'true'
            }),
            'amount_lost': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'class': 'w-full px-4 py-3 border border-coolGray rounded-lg focus:ring-2 focus:ring-cyan focus:border-transparent transition',
                'required': 'true'
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
        self.user = kwargs.pop('user', None)  # Get user from form initialization
        super().__init__(*args, **kwargs)
        
        # Remove currency field entirely since we'll use user's preferred currency
        if 'currency' in self.fields:
            del self.fields['currency']
        
        # Make scam-specific fields not required initially
        scam_specific_fields = [
            'blockchain', 'victim_wallet', 'scammer_wallet', 'transaction_hash',
            'exchange_used', 'bank_name', 'account_debited', 'beneficiary_details',
            'suspect_email', 'suspect_phone', 'suspect_website'
        ]
        for field in scam_specific_fields:
            self.fields[field].required = False
    
    def clean_amount_lost(self):
        """Validate amount lost"""
        amount_lost = self.cleaned_data.get('amount_lost')
        if amount_lost and amount_lost <= 0:
            raise forms.ValidationError('Amount lost must be greater than 0.')
        return amount_lost
    
    def clean_incident_date(self):
        """Validate incident date is not in the future"""
        incident_date = self.cleaned_data.get('incident_date')
        if incident_date and incident_date > timezone.now().date():
            raise forms.ValidationError('Incident date cannot be in the future.')
        return incident_date
    
    def save(self, commit=True):
        case = super().save(commit=False)
        # Set currency to user's preferred currency automatically
        if self.user:
            case.currency = self.user.preferred_currency
        if commit:
            case.save()
        return case

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

# core/forms.py - UPDATE THE EnhancedUserUpdateForm

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
        help_texts = {
            'preferred_currency': 'All amounts will be displayed in this currency',
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