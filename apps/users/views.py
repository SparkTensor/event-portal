from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
# To import account activation token function to create tokens
from .tokens import account_activation_token
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.urls import NoReverseMatch, reverse
from .utils import EmailThread
from .utils import generate_unique_username
# reset password generators
from django.contrib.auth.tokens import PasswordResetTokenGenerator

# To import settings for sending mail
from django.conf import settings

User = get_user_model()

# Create your views here.
def epusers_signup(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email_raw = request.POST['email']
        # To clean the email
        email = email_raw.strip().lower() if email_raw else None
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        role = request.POST.get('role')

        if password == confirm_password:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'The email address you provided already exists')
                return redirect('epusers_signup')
            else:
                username = generate_unique_username(first_name)
                ep_user = User.objects.create_user(username, email, password)
                ep_user.last_name = last_name
                ep_user.first_name = first_name

                # --- CHANGE 3: Set the user role based on form selection ---
                if role == 'organizer':
                    ep_user.is_organizer = True
                    # Organizers are a distinct role, so we set attendee to False.
                    ep_user.is_attendee = False
                else: # Defaults to attendee
                    ep_user.is_organizer = False
                    ep_user.is_attendee = True

                ep_user.is_active = False
                ep_user.save()

                # Code to prepare and send verification email to new users
                current_site = get_current_site(request)
                mail_subject = 'EFS Team - Verify your email address'
                message = render_to_string('users/epusers_email_activation_message.html', {
                    #Context - information to (include) send with message
                    'user': ep_user, 
                    'domain':current_site.domain,
                    'user_id':urlsafe_base64_encode(force_bytes(ep_user.pk)),
                    'token':account_activation_token.make_token(ep_user),
                    }
                )
                receiving_email = ep_user.email
                # The Email message
                email_message = EmailMessage(mail_subject, message, from_email = settings.DEFAULT_FROM_EMAIL, to=[receiving_email])
                # Add tags for tracking in Mailchimp/Mandrill
                #email_message.tags = ["user_activation", "signup"]
                EmailThread(email_message).start()

                return redirect('epusers_verification_email_sent')

    return render(request, 'users/epusers_signup.html')

def epusers_verification_email_sent(request):
    return render(request, 'users/epusers_verification_email_sent.html')


class epusers_activate_account(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # Check if the user exists and the token is valid
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            
            # Redirect to your dedicated "Account Activated" success page
            return redirect('epusers_account_activated') # This name comes from your urls.py
        
        else:
            # For invalid links, render a simple "activation failed" page
            # This is better than a plain HttpResponse
            return render(request, 'users/epusers_activation_failed.html')


def epusers_account_activated(request):
    return render(request, 'users/epusers_account_activated.html')

def epusers_activation_failed(request):
    return render(request, 'users/epusers_activation_failed.html')

def epusers_login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'Invalid login details.')
            return redirect('epusers_login')

        # Use the username to authenticate
        user = authenticate(request, username=user_obj.username, password=password)

        if user is not None and user.is_active:
            login(request, user)

            if user.is_attendee:
                return redirect("https://economicforumseries.com/")
            elif user.is_organizer:
                return redirect('epusers_dashboard')
            else:
                messages.warning(request, 'User role not defined.')
                return redirect('epusers_dashboard')
        else:
            messages.error(request, 'Invalid login details.')
            return redirect('epusers_login')

    return render(request, 'users/epusers_login.html')




class epusers_request_reset_email(View):
    def get(self, request):
        return render(request, 'users/epusers_request_reset_email.html')
    
    def post(self, request):
        reset_email_raw = request.POST.get('email') # Use .get() to avoid errors if email is missing
        reset_email = reset_email_raw.strip().lower() if reset_email_raw else None
        
        # Security Best Practice:
        # Always redirect to a confirmation page, even if the email doesn't exist.
        # This prevents attackers from figuring out which emails are registered.
        
        if reset_email:
            user_queryset = User.objects.filter(email=reset_email)

            if user_queryset.exists():
                user = user_queryset.first() # Get the actual user object
                current_site = get_current_site(request)
                email_subject = 'Reset Your Password'
                
                # IMPORTANT: The URL must point to your NEW password reset view
                # Let's assume you will call its URL 'epusers_reset_password_confirm'
                message = render_to_string('users/epusers_reset_password_message.html', {
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': PasswordResetTokenGenerator().make_token(user),
                    'user': user # Pass the user to the template for personalization
                })

                email_message = EmailMessage(
                    email_subject, 
                    message, 
                    from_email=settings.DEFAULT_FROM_EMAIL, 
                    to=[reset_email]
                )
                EmailThread(email_message).start()

        # Redirect to the "sent" page to complete the process
        return redirect('epusers_reset_email_sent')
    
def epusers_reset_email_sent(request):
    return render(request, 'users/epusers_reset_email_sent.html')

# The page to handle the click form the email containing the password reset email + The change password form
class epusers_change_password(View):
    
    def get(self, request, uidb64, token):
        try:
            # First, try to decode the user ID and find the user
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            # Then, check if the token is valid for that user
            if not PasswordResetTokenGenerator().check_token(user, token):
                # If token is invalid, show a clear error page
                messages.error(request, "This password reset link is invalid or has expired.")
                return redirect('epusers_request_reset_email') # Redirect to the start

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            # If the user doesn't exist or uidb64 is bad, treat it as an invalid link
            messages.error(request, "This password reset link is invalid or has expired.")
            return redirect('epusers_request_reset_email')

        # If everything is valid, render the form
        context = {
            'uidb64': uidb64,
            'token': token
        }
        # The template name should match your file system
        return render(request, 'users/epusers_change_password.html', context)
    
    def post(self, request, uidb64, token):
        # --- CRITICAL: RE-VALIDATE THE USER AND TOKEN ON POST ---
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.error(request, "This password reset link is invalid or has expired.")
                return redirect('epusers_request_reset_email')

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(request, "This password reset link is invalid or has expired.")
            return redirect('epusers_request_reset_email')
        
        # --- NOW, PROCEED WITH PASSWORD VALIDATION ---
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')

        if new_password != confirm_new_password:
            messages.warning(request, 'Passwords do not match.')
            # We need to re-render the page, passing context so the form URL works
            context = {'uidb64': uidb64, 'token': token}
            return render(request, 'users/epusers_change_password.html', context)
        
        # If passwords match, set the new password and save
        user.set_password(new_password)
        user.save()

        messages.success(request, "Your password has been reset successfully! You can now log in.")
        
        # Redirect to the login page
        return redirect('epusers_login') # Use the name of your login URL
    

def epusers_dashboard(request):
    return render(request, 'users/epusers_dashboard.html')