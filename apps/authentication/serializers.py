"""
Authentication serializers for AI-Powered Personal Stylist & Wardrobe Manager
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
import re

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'name', 'password', 'confirm_password')
        
    def validate_email(self, value):
        """Validate email is unique and valid format"""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()
    
    def validate_name(self, value):
        """Validate name format"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        
        # Allow letters, spaces, hyphens, and apostrophes
        if not re.match(r"^[a-zA-Z\s\-']+$", value):
            raise serializers.ValidationError("Name can only contain letters, spaces, hyphens, and apostrophes.")
        
        return value.strip()
    
    def validate(self, attrs):
        """Cross-field validation"""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        
        # Remove confirm_password as it's not part of the model
        attrs.pop('confirm_password', None)
        return attrs
    
    def create(self, validated_data):
        """Create new user with email activation required"""
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
            email_verified=False  # Require email verification
        )
        
        # Create user profile
        from apps.authentication.models import UserProfile
        UserProfile.objects.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Authenticate user and validate account status"""
        email = attrs.get('email', '').lower()
        password = attrs.get('password', '')
        
        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")
        
        # Check if account is locked
        if user.is_account_locked:
            raise serializers.ValidationError("Account is temporarily locked due to too many failed login attempts.")
        
        # Check if email is verified
        if not user.email_verified:
            raise serializers.ValidationError("Please verify your email address before logging in.")
        
        # Authenticate user
        if not user.check_password(password):
            # Increment failed login attempts
            user.failed_login_attempts += 1
            
            # Lock account if too many failed attempts
            from django.conf import settings
            max_attempts = getattr(settings, 'ACCOUNT_LOCKOUT_THRESHOLD', 5)
            if user.failed_login_attempts >= max_attempts:
                lockout_duration = getattr(settings, 'ACCOUNT_LOCKOUT_DURATION', 1800)  # 30 minutes
                user.lock_account(lockout_duration)
            
            user.save(update_fields=['failed_login_attempts', 'account_locked_until'])
            raise serializers.ValidationError("Invalid credentials.")
        
        # Check if user is active
        if not user.is_active:
            raise serializers.ValidationError("User account is inactive.")
        
        # Reset failed login attempts on successful login
        if user.failed_login_attempts > 0:
            user.failed_login_attempts = 0
            user.save(update_fields=['failed_login_attempts'])
        
        attrs['user'] = user
        return attrs


class EmailActivationSerializer(serializers.Serializer):
    """
    Serializer for email activation
    """
    token = serializers.CharField()
    
    def validate_token(self, value):
        """Validate activation token"""
        from .authentication import TokenManager
        import jwt
        
        try:
            payload = TokenManager.decode_token(value, 'activation')
            
            try:
                user = User.objects.get(user_id=payload['user_id'])
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid token.")
            
            if user.email_verified:
                raise serializers.ValidationError("Email is already verified.")
            
            # Store user for use in view
            self.context['user'] = user
            return value
            
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError("Token has expired. Please request a new activation link.")
        except jwt.InvalidTokenError:
            raise serializers.ValidationError("Invalid token.")


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for password reset request
    """
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Validate email exists"""
        try:
            user = User.objects.get(email=value.lower())
            self.context['user'] = user
            return value.lower()
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            return value.lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation
    """
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    def validate_token(self, value):
        """Validate reset token"""
        from .authentication import TokenManager
        import jwt
        
        try:
            payload = TokenManager.decode_token(value, 'password_reset')
            
            try:
                user = User.objects.get(user_id=payload['user_id'])
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid token.")
            
            # Store user for use in view
            self.context['user'] = user
            return value
            
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError("Token has expired. Please request a new password reset.")
        except jwt.InvalidTokenError:
            raise serializers.ValidationError("Invalid token.")
    
    def validate(self, attrs):
        """Cross-field validation"""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        
        attrs.pop('confirm_password', None)
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information
    """
    class Meta:
        model = User
        fields = ('user_id', 'email', 'name', 'email_verified', 'created_at', 'last_login')
        read_only_fields = ('user_id', 'email_verified', 'created_at', 'last_login')


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        from apps.authentication.models import UserProfile
        model = UserProfile
        fields = (
            'user', 'style_prefs', 'last_known_location', 
            'preferred_weather_unit', 'user_timezone',
            'data_processing_consent', 'marketing_emails_consent',
            'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change (when user is logged in)
    """
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    def validate_current_password(self, value):
        """Validate current password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("New passwords do not match.")
        
        if attrs['current_password'] == attrs['new_password']:
            raise serializers.ValidationError("New password must be different from current password.")
        
        attrs.pop('confirm_password', None)
        return attrs


class TokenRefreshSerializer(serializers.Serializer):
    """
    Serializer for token refresh
    """
    refresh_token = serializers.CharField()
    
    def validate_refresh_token(self, value):
        """Validate refresh token and generate new access token"""
        from .authentication import TokenManager
        import jwt
        
        try:
            new_access_token = TokenManager.refresh_access_token(value)
            self.context['access_token'] = new_access_token
            return value
        except jwt.InvalidTokenError:
            raise serializers.ValidationError("Invalid or expired refresh token.")
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError("Refresh token has expired. Please log in again.")


class AccountSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for account settings updates
    """
    class Meta:
        model = User
        fields = ('name',)
    
    def validate_name(self, value):
        """Validate name format"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        
        if not re.match(r"^[a-zA-Z\s\-']+$", value):
            raise serializers.ValidationError("Name can only contain letters, spaces, hyphens, and apostrophes.")
        
        return value.strip()
