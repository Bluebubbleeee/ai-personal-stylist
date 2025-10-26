"""
Recommendations models for AI-Powered Personal Stylist & Wardrobe Manager
"""

import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings


class OutfitSuggestion(models.Model):
    """
    Model representing AI-generated outfit suggestions
    Based on the database schema from steps.txt
    """
    
    WEATHER_CONDITION_CHOICES = [
        ('sunny', 'Sunny'),
        ('cloudy', 'Cloudy'),
        ('rainy', 'Rainy'),
        ('snowy', 'Snowy'),
        ('windy', 'Windy'),
        ('foggy', 'Foggy'),
        ('stormy', 'Stormy'),
        ('clear', 'Clear'),
        ('overcast', 'Overcast'),
        ('unknown', 'Unknown'),
    ]
    
    suggestion_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='outfit_suggestions'
    )
    
    # User input
    prompt = models.TextField(help_text="User's style prompt (e.g., 'smart casual for dinner')")
    location = models.CharField(max_length=255, blank=True, help_text="Location for weather context")
    
    # Weather data at time of suggestion
    weather = models.JSONField(
        default=dict,
        help_text="Weather data used for the suggestion (temperature, condition, etc.)"
    )
    
    # Outfit composition
    items_included = models.JSONField(
        default=list,
        help_text="List of clothing item IDs included in this suggestion"
    )
    outfit_structure = models.JSONField(
        default=dict,
        help_text="Structured representation of the outfit (tops, bottoms, shoes, etc.)"
    )
    
    # AI metadata
    ai_rationale = models.TextField(
        help_text="AI's explanation for why this outfit was suggested"
    )
    confidence_score = models.FloatField(
        null=True,
        blank=True,
        help_text="AI confidence score for this suggestion (0-1)"
    )
    model_version = models.CharField(
        max_length=50,
        blank=True,
        help_text="Version of the AI model used"
    )
    
    # Scoring components (for debugging and improvement)
    weather_score = models.FloatField(null=True, blank=True)
    prompt_score = models.FloatField(null=True, blank=True)
    color_harmony_score = models.FloatField(null=True, blank=True)
    user_affinity_score = models.FloatField(null=True, blank=True)
    recency_penalty = models.FloatField(null=True, blank=True)
    final_score = models.FloatField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'outfit_suggestions'
        verbose_name = 'Outfit Suggestion'
        verbose_name_plural = 'Outfit Suggestions'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['confidence_score']),
            models.Index(fields=['final_score']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Outfit suggestion for {self.user.name} - {self.prompt[:50]}"
    
    @property
    def temperature(self):
        """Extract temperature from weather data"""
        return self.weather.get('temperature')
    
    @property
    def weather_condition(self):
        """Extract weather condition from weather data"""
        return self.weather.get('condition', 'unknown')
    
    @property
    def item_count(self):
        """Number of items in this suggestion"""
        return len(self.items_included)
    
    def get_clothing_items(self):
        """Get the actual ClothingItem objects for this suggestion"""
        from apps.wardrobe.models import ClothingItem
        return ClothingItem.objects.filter(item_id__in=self.items_included)


class StyleVector(models.Model):
    """
    Model representing user style preferences as a vector
    Used for personalization via Exponential Moving Average (EMA)
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='style_vector'
    )
    
    # Style preference vectors (stored as JSON for flexibility)
    vector_data = models.JSONField(
        default=dict,
        help_text="Vector representation of user's style preferences"
    )
    
    # EMA parameters
    learning_rate = models.FloatField(
        default=0.1,
        help_text="Learning rate for EMA updates (0-1)"
    )
    
    # Statistics
    total_feedback_count = models.IntegerField(default=0)
    last_updated = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'style_vectors'
        verbose_name = 'Style Vector'
        verbose_name_plural = 'Style Vectors'
    
    def __str__(self):
        return f"Style Vector for {self.user.name}"
    
    def update_with_feedback(self, outfit_features, rating):
        """
        Update style vector using EMA based on user feedback
        
        Args:
            outfit_features (dict): Features extracted from the rated outfit
            rating (float): User rating (-1 to 1, where -1 is thumbs down, 1 is thumbs up)
        """
        if not self.vector_data:
            # Initialize with the first feedback
            self.vector_data = outfit_features.copy()
        else:
            # Update using EMA: new_value = (1-α) * old_value + α * new_value
            # But we modify based on rating: if negative, we subtract instead of add
            for feature, value in outfit_features.items():
                old_value = self.vector_data.get(feature, 0)
                if rating > 0:
                    # Positive feedback: move towards this feature
                    self.vector_data[feature] = (1 - self.learning_rate) * old_value + self.learning_rate * value
                else:
                    # Negative feedback: move away from this feature
                    self.vector_data[feature] = (1 - self.learning_rate) * old_value - self.learning_rate * value * 0.5
        
        self.total_feedback_count += 1
        self.last_updated = timezone.now()
        self.save()
    
    def get_feature_preference(self, feature):
        """Get preference score for a specific feature"""
        return self.vector_data.get(feature, 0)
    
    def get_top_preferences(self, limit=10):
        """Get top preferred features"""
        if not self.vector_data:
            return []
        
        sorted_prefs = sorted(
            self.vector_data.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_prefs[:limit]


class RecommendationSession(models.Model):
    """
    Model to track recommendation sessions for analytics and debugging
    """
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recommendation_sessions'
    )
    
    # Session input
    original_prompt = models.TextField()
    location = models.CharField(max_length=255, blank=True)
    weather_data = models.JSONField(default=dict)
    
    # Processing metadata
    processing_time_ms = models.IntegerField(null=True, blank=True)
    wardrobe_items_considered = models.IntegerField(default=0)
    total_combinations_scored = models.IntegerField(default=0)
    
    # Results
    suggestions_generated = models.IntegerField(default=0)
    suggestions = models.ManyToManyField(
        OutfitSuggestion,
        related_name='sessions',
        blank=True
    )
    
    # External API calls
    weather_api_called = models.BooleanField(default=False)
    weather_api_response_time_ms = models.IntegerField(null=True, blank=True)
    ai_api_called = models.BooleanField(default=False)
    ai_api_response_time_ms = models.IntegerField(null=True, blank=True)
    
    # Status
    completed_successfully = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'recommendation_sessions'
        verbose_name = 'Recommendation Session'
        verbose_name_plural = 'Recommendation Sessions'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['completed_successfully']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Session {self.session_id} for {self.user.name}"
    
    def mark_completed(self, success=True, error_message=""):
        """Mark the session as completed"""
        self.completed_successfully = success
        self.completed_at = timezone.now()
        if error_message:
            self.error_message = error_message
        self.save()
    
    @property
    def duration_ms(self):
        """Calculate session duration in milliseconds"""
        if self.completed_at:
            delta = self.completed_at - self.created_at
            return int(delta.total_seconds() * 1000)
        return None


class WeatherCache(models.Model):
    """
    Model to cache weather data to reduce API calls
    """
    location = models.CharField(max_length=255, db_index=True)
    weather_data = models.JSONField(default=dict)
    
    # Cache metadata
    api_provider = models.CharField(max_length=50, default='unknown')
    cache_key = models.CharField(max_length=255, unique=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'weather_cache'
        verbose_name = 'Weather Cache Entry'
        verbose_name_plural = 'Weather Cache Entries'
        indexes = [
            models.Index(fields=['location', 'expires_at']),
            models.Index(fields=['cache_key']),
        ]
    
    def __str__(self):
        return f"Weather cache for {self.location}"
    
    @property
    def is_expired(self):
        """Check if cache entry has expired"""
        return timezone.now() > self.expires_at
    
    @classmethod
    def get_cached_weather(cls, location):
        """Get valid cached weather data for a location"""
        try:
            cache_entry = cls.objects.get(
                location=location,
                expires_at__gt=timezone.now()
            )
            return cache_entry.weather_data
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def cache_weather_data(cls, location, weather_data, cache_duration_minutes=60):
        """Cache weather data for a location"""
        cache_key = f"weather_{location}_{timezone.now().strftime('%Y%m%d%H')}"
        expires_at = timezone.now() + timezone.timedelta(minutes=cache_duration_minutes)
        
        # Update or create cache entry
        cache_entry, created = cls.objects.update_or_create(
            cache_key=cache_key,
            defaults={
                'location': location,
                'weather_data': weather_data,
                'expires_at': expires_at,
            }
        )
        return cache_entry