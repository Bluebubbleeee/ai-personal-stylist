"""
Authentication models for AI-Powered Personal Stylist & Wardrobe Manager
"""

import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
# JSONField is built into Django 3.1+ models
from django.core.validators import EmailValidator


class CustomUserManager(BaseUserManager):
    """Custom user manager for User model with email as unique identifier"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('email_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model using email as the unique identifier
    Based on the database schema from steps.txt
    """
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text="User's email address - used for login"
    )
    name = models.CharField(max_length=100, help_text="User's display name")
    password_hash = models.CharField(max_length=128, help_text="Argon2id hashed password")
    email_verified = models.BooleanField(
        default=False,
        help_text="Whether user has verified their email address"
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Account security
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    
    # Use email as the unique identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    objects = CustomUserManager()
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
            models.Index(fields=['email_verified']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.email})"
    
    @property
    def is_account_locked(self):
        """Check if account is currently locked"""
        if self.account_locked_until:
            return timezone.now() < self.account_locked_until
        return False
    
    def lock_account(self, duration_seconds=1800):  # 30 minutes default
        """Lock the account for specified duration"""
        self.account_locked_until = timezone.now() + timezone.timedelta(seconds=duration_seconds)
        self.save(update_fields=['account_locked_until'])
    
    def unlock_account(self):
        """Unlock the account and reset failed login attempts"""
        self.account_locked_until = None
        self.failed_login_attempts = 0
        self.save(update_fields=['account_locked_until', 'failed_login_attempts'])


class UserProfile(models.Model):
    """
    Extended user profile for storing style preferences and location
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='profile'
    )
    style_prefs = models.JSONField(
        default=dict,
        help_text="JSON object storing user's style preferences and settings"
    )
    last_known_location = models.CharField(
        max_length=255,
        blank=True,
        help_text="User's last known location for weather-based recommendations"
    )
    
    # Preference settings
    preferred_weather_unit = models.CharField(
        max_length=10,
        choices=[('celsius', 'Celsius'), ('fahrenheit', 'Fahrenheit')],
        default='celsius'
    )
    user_timezone = models.CharField(max_length=50, default='UTC')
    
    # Privacy settings
    data_processing_consent = models.BooleanField(default=False)
    marketing_emails_consent = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.name}'s Profile"


class EmailActivationToken(models.Model):
    """
    Model to store email activation tokens
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activation_tokens')
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'email_activation_tokens'
        verbose_name = 'Email Activation Token'
        verbose_name_plural = 'Email Activation Tokens'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Activation token for {self.user.email}"
    
    @property
    def is_expired(self):
        """Check if token has expired"""
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if token is valid (not used, not expired, active)"""
        return self.is_active and not self.used_at and not self.is_expired
    
    def mark_as_used(self):
        """Mark token as used"""
        self.used_at = timezone.now()
        self.is_active = False
        self.save(update_fields=['used_at', 'is_active'])


class PasswordResetToken(models.Model):
    """
    Model to store password reset tokens
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'password_reset_tokens'
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Reset token for {self.user.email}"
    
    @property
    def is_expired(self):
        """Check if token has expired"""
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if token is valid (not used, not expired, active)"""
        return self.is_active and not self.used_at and not self.is_expired
    
    def mark_as_used(self):
        """Mark token as used"""
        self.used_at = timezone.now()
        self.is_active = False
        self.save(update_fields=['used_at', 'is_active'])