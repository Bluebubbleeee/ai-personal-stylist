"""
Authentication views for AI-Powered Personal Stylist & Wardrobe Manager
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from apps.common.email_service import send_activation_email, send_password_reset_email
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import jwt
import logging

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    EmailActivationSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    UserProfileSerializer
)
from .authentication import TokenManager
from .models import EmailActivationToken, PasswordResetToken, UserProfile
from apps.common.models import AuditLog

logger = logging.getLogger(__name__)
User = get_user_model()


# ==============================================================================
# API ENDPOINTS
# ==============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def register_api(request):
    """API endpoint for user registration"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Generate activation token
        activation_token = TokenManager.generate_activation_token(user)
        
        # Send activation email
        send_activation_email(user, activation_token)
        
        # Log the registration
        AuditLog.objects.create(
            user=user,
            action='user_registered',
            resource_type='user',
            resource_id=str(user.user_id),
            ip_address=get_client_ip(request),
            metadata={'email': user.email}
        )
        
        return Response({
            'message': 'Registration successful. Please check your email to activate your account.',
            'user_id': user.user_id
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    """API endpoint for user login"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Generate tokens
        access_token = TokenManager.generate_access_token(user)
        refresh_token = TokenManager.generate_refresh_token(user)
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        return Response({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'user_id': user.user_id,
                'email': user.email,
                'name': user.name,
            }
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# WEB VIEWS
# ==============================================================================

class HomeView(View):
    """Homepage view"""
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'authentication/home.html')


class RegisterView(View):
    """User registration view"""
    @method_decorator(never_cache)
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'authentication/register.html')

    @method_decorator(csrf_protect)
    def post(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        
        serializer = UserRegistrationSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate and send activation email
            activation_token = TokenManager.generate_activation_token(user)
            send_activation_email(user, activation_token)
            
            messages.success(request, 'Registration successful! Please check your email to activate your account.')
            return redirect('login')
        else:
            for field, errors in serializer.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return render(request, 'authentication/register.html')


class LoginView(View):
    """User login view"""
    @method_decorator(never_cache)
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'authentication/login.html')

    @method_decorator(csrf_protect)
    def post(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        
        serializer = UserLoginSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            # Use Django sessions for web interface
            from django.contrib.auth import login
            login(request, user)
            
            messages.success(request, f'Welcome back, {user.name}!')
            return redirect('dashboard')
        else:
            for field, errors in serializer.errors.items():
                for error in errors:
                    messages.error(request, error)
            return render(request, 'authentication/login.html')


class EmailActivationView(View):
    """Email activation view"""
    def get(self, request):
        token = request.GET.get('token')
        if not token:
            messages.error(request, 'Invalid activation link.')
            return redirect('login')
        
        try:
            payload = TokenManager.decode_token(token, 'activation')
            user = User.objects.get(user_id=payload['user_id'])
            
            if user.email_verified:
                messages.info(request, 'Your email is already verified.')
                return redirect('login')
            
            user.email_verified = True
            user.save(update_fields=['email_verified'])
            
            messages.success(request, 'Email activated successfully! You can now log in.')
            return redirect('login')
            
        except (jwt.InvalidTokenError, jwt.ExpiredSignatureError, User.DoesNotExist):
            messages.error(request, 'Invalid or expired activation link.')
            return redirect('login')


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def send_activation_email(user, token):
    """Send email activation email"""
    try:
        activation_url = f"http://127.0.0.1:8000/auth/activate/?token={token}"
        
        subject = 'Activate your AI Stylist account'
        message = f"""
        Hi {user.name},
        
        Welcome to AI Stylist! Please click the link below to activate your account:
        
        {activation_url}
        
        This link will expire in 24 hours.
        
        Best regards,
        AI Stylist Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Activation email sent to {user.email}")
        
    except Exception as e:
        logger.error(f"Failed to send activation email to {user.email}: {str(e)}")


def send_password_reset_email(user, token):
    """Send password reset email"""
    try:
        reset_url = f"http://127.0.0.1:8000/auth/password-reset-confirm/?token={token}"
        
        subject = 'Reset your AI Stylist password'
        message = f"""
        Hi {user.name},
        
        You requested a password reset for your AI Stylist account. Click the link below to reset your password:
        
        {reset_url}
        
        This link will expire in 1 hour. If you didn't request this, please ignore this email.
        
        Best regards,
        AI Stylist Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Password reset email sent to {user.email}")
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_api(request):
    """API logout endpoint"""
    from django.contrib.auth import logout
    logout(request)
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)


class LogoutView(View):
    """Web logout view"""
    def get(self, request):
        if request.user.is_authenticated:
            from django.contrib.auth import logout
            logout(request)
            messages.success(request, 'You have been logged out successfully.')
        return redirect('home')


class SettingsView(View):
    """User settings/profile management view"""
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        context = {
            'user': request.user,
            'profile': profile,
        }
        return render(request, 'authentication/settings.html', context)
    
    @method_decorator(csrf_protect)
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Handle different form submissions
        action = request.POST.get('action')
        
        if action == 'update_profile':
            return self._update_profile(request)
        elif action == 'change_password':
            return self._change_password(request)
        elif action == 'update_preferences':
            return self._update_preferences(request)
        else:
            messages.error(request, 'Invalid action.')
            return redirect('settings')
    
    def _update_profile(self, request):
        """Update user profile information"""
        try:
            # Update basic user info
            name = request.POST.get('name', '').strip()
            if name:
                request.user.name = name
                request.user.save(update_fields=['name'])
            
            # Get or create profile
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            
            # Update profile fields
            profile.last_known_location = request.POST.get('last_known_location', '').strip()
            profile.preferred_weather_unit = request.POST.get('preferred_weather_unit', 'celsius')
            profile.user_timezone = request.POST.get('user_timezone', 'UTC')
            profile.data_processing_consent = request.POST.get('data_processing_consent') == 'on'
            profile.marketing_emails_consent = request.POST.get('marketing_emails_consent') == 'on'
            profile.save()
            
            messages.success(request, 'Profile updated successfully!')
            
        except Exception as e:
            logger.error(f"Error updating profile for user {request.user.email}: {str(e)}")
            messages.error(request, 'An error occurred while updating your profile.')
        
        return redirect('settings')
    
    def _change_password(self, request):
        """Change user password"""
        try:
            current_password = request.POST.get('current_password', '')
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')
            
            # Validate current password
            if not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
                return redirect('settings')
            
            # Validate new password
            if not new_password:
                messages.error(request, 'New password is required.')
                return redirect('settings')
            
            if new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
                return redirect('settings')
            
            if len(new_password) < 8:
                messages.error(request, 'New password must be at least 8 characters long.')
                return redirect('settings')
            
            # Update password
            request.user.set_password(new_password)
            request.user.save()
            
            messages.success(request, 'Password changed successfully!')
            
        except Exception as e:
            logger.error(f"Error changing password for user {request.user.email}: {str(e)}")
            messages.error(request, 'An error occurred while changing your password.')
        
        return redirect('settings')
    
    def _update_preferences(self, request):
        """Update user style preferences"""
        try:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            
            # Update style preferences (stored as JSON)
            style_prefs = profile.style_prefs or {}
            
            # Update various preferences
            style_prefs['favorite_colors'] = request.POST.getlist('favorite_colors', [])
            style_prefs['favorite_styles'] = request.POST.getlist('favorite_styles', [])
            style_prefs['favorite_occasions'] = request.POST.getlist('favorite_occasions', [])
            style_prefs['size_preference'] = request.POST.get('size_preference', '')
            style_prefs['comfort_level'] = request.POST.get('comfort_level', '')
            
            profile.style_prefs = style_prefs
            profile.save()
            
            messages.success(request, 'Style preferences updated successfully!')
            
        except Exception as e:
            logger.error(f"Error updating preferences for user {request.user.email}: {str(e)}")
            messages.error(request, 'An error occurred while updating your preferences.')
        
        return redirect('settings')