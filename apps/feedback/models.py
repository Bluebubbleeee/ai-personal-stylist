"""
Feedback models for AI-Powered Personal Stylist & Wardrobe Manager
"""

import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class OutfitFeedback(models.Model):
    """
    Model representing user feedback on outfit suggestions or planned outfits
    Based on the database schema from steps.txt (Feedback table)
    """
    
    RATING_CHOICES = [
        (-1, 'Thumbs Down'),
        (0, 'Neutral'),
        (1, 'Thumbs Up'),
    ]
    
    STAR_RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    FEEDBACK_TYPE_CHOICES = [
        ('suggestion', 'AI Suggestion'),
        ('planned_outfit', 'Planned Outfit'),
        ('worn_outfit', 'Actually Worn'),
        ('template', 'Template'),
    ]
    
    feedback_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    
    # What the feedback is about
    feedback_type = models.CharField(
        max_length=20,
        choices=FEEDBACK_TYPE_CHOICES,
        default='suggestion'
    )
    outfit_id = models.UUIDField(
        help_text="ID of the outfit suggestion, plan, or template being rated"
    )
    
    # Feedback ratings
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        help_text="Thumbs up/down rating (-1, 0, 1)"
    )
    star_rating = models.IntegerField(
        choices=STAR_RATING_CHOICES,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Optional 1-5 star rating"
    )
    
    # Detailed feedback
    comment = models.TextField(
        blank=True,
        help_text="Optional user comment about the outfit"
    )
    
    # Context and metadata
    occasion_context = models.CharField(
        max_length=255,
        blank=True,
        help_text="What occasion the outfit was for"
    )
    outfit_features = models.JSONField(
        default=dict,
        help_text="Extracted features from the outfit for ML learning"
    )
    processed_for_learning = models.BooleanField(
        default=False,
        help_text="Whether this feedback has been processed for style vector updates"
    )
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'feedback'
        verbose_name = 'Outfit Feedback'
        verbose_name_plural = 'Outfit Feedback'
        unique_together = [['user', 'outfit_id', 'feedback_type']]
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['user', 'rating']),
            models.Index(fields=['feedback_type']),
            models.Index(fields=['processed_for_learning']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        rating_text = dict(self.RATING_CHOICES)[self.rating]
        return f"Feedback by {self.user.name}: {rating_text}"
    
    @property
    def is_positive(self):
        return self.rating > 0
    
    @property
    def is_negative(self):
        return self.rating < 0
    
    @property
    def is_neutral(self):
        return self.rating == 0