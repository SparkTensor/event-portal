from django.urls import path
from . import views

urlpatterns = [
    path('/signup', views.epusers_signup, name='epusers_signup'),
    path('login/', views.epusers_login, name='epusers_login'),
    path('signup/email_verification/', views.epusers_verification_email_sent, name='epusers_verification_email_sent'),
    # Url to send the activation email
    path('signup/email_verification/account_activated/', views.epusers_account_activated, name='epusers_account_activated'),
    # For faild email verification - or account activation
    path('signup/email_verification/activation_failed/', views.epusers_activation_failed, name='epusers_activation_failed'),
    # To activate the email in the view 
    path('activate/<uidb64>/<token>', views.epusers_activate_account.as_view(), name='epusers_activate_account'),
    # Forgot password: Get email + verify and link to password reset page
    path('forgot_password/', views.epusers_request_reset_email.as_view(), name='epusers_request_reset_email'),
    # Password reset email sent
    path('forgot_password/reset_email_sent/', views.epusers_reset_email_sent, name='epusers_reset_email_sent'),
    path('forgot_password/set_password/<uidb64>/<token>', views.epusers_change_password.as_view(), name='epusers_change_password'),
    #path('logout/', views.epusers_logout, name='epusers_logout'),

    # For the Custom Dashboard
    path('', views.epusers_dashboard, name='epusers_dashboard'),
]
