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