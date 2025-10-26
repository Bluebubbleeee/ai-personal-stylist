"""
Common models for AI-Powered Personal Stylist & Wardrobe Manager
"""

import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings


class AuditLog(models.Model):
    """
    Model for audit logging to track user actions
    """
    log_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    
    # Action information
    action = models.CharField(max_length=100, help_text="Action performed")
    resource_type = models.CharField(max_length=50, help_text="Type of resource affected")
    resource_id = models.CharField(max_length=100, help_text="ID of the affected resource")
    
    # Request information
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Additional context
    metadata = models.JSONField(
        default=dict,
        help_text="Additional context data"
    )
    
    # Timestamps
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        user_str = self.user.email if self.user else 'Anonymous'
        return f"{user_str} - {self.action} on {self.resource_type}"


class SystemSettings(models.Model):
    """
    Model for storing system-wide settings
    """
    key = models.CharField(max_length=100, unique=True, primary_key=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    
    # Metadata
    is_public = models.BooleanField(
        default=False,
        help_text="Whether this setting can be viewed by regular users"
    )
    is_editable = models.BooleanField(
        default=True,
        help_text="Whether this setting can be modified"
    )
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_settings'
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'
        ordering = ['key']
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}"


class APIUsageLog(models.Model):
    """
    Model for tracking external API usage
    """
    log_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='api_usage_logs'
    )
    
    # API information
    api_provider = models.CharField(max_length=50, help_text="Name of the API provider")
    api_endpoint = models.CharField(max_length=255, help_text="API endpoint called")
    request_method = models.CharField(max_length=10, default='GET')
    
    # Request/Response data
    request_data = models.JSONField(default=dict, blank=True)
    response_status_code = models.IntegerField(null=True, blank=True)
    response_time_ms = models.IntegerField(null=True, blank=True)
    
    # Status
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    # Timestamps
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    
    class Meta:
        db_table = 'api_usage_logs'
        verbose_name = 'API Usage Log'
        verbose_name_plural = 'API Usage Logs'
        indexes = [
            models.Index(fields=['api_provider', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['success']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.api_provider} - {self.api_endpoint} ({self.response_status_code})"