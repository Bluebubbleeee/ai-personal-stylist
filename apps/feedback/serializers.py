"""
Feedback serializers for AI-Powered Personal Stylist & Wardrobe Manager
"""

from rest_framework import serializers
from .models import OutfitFeedback
from apps.recommendations.serializers import OutfitSuggestionSerializer


class OutfitFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for outfit feedback"""
    
    suggestion = OutfitSuggestionSerializer(read_only=True)
    suggestion_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = OutfitFeedback
        fields = [
            'feedback_id', 'suggestion', 'suggestion_id', 'feedback_type',
            'rating', 'comments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['feedback_id', 'created_at', 'updated_at']
    
    def validate_feedback_type(self, value):
        """Validate feedback type"""
        if value not in ['like', 'dislike', 'rating']:
            raise serializers.ValidationError("Feedback type must be 'like', 'dislike', or 'rating'")
        return value
    
    def validate_rating(self, value):
        """Validate rating value"""
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
    
    def validate(self, data):
        """Custom validation"""
        feedback_type = data.get('feedback_type')
        rating = data.get('rating')
        
        if feedback_type == 'rating' and rating is None:
            raise serializers.ValidationError("Rating is required when feedback_type is 'rating'")
        
        if feedback_type in ['like', 'dislike'] and rating is not None:
            raise serializers.ValidationError("Rating should not be provided for like/dislike feedback")
        
        return data


class StylePreferencesSerializer(serializers.Serializer):
    """Serializer for user style preferences"""
    
    colors = serializers.DictField(child=serializers.FloatField(), required=False)
    categories = serializers.DictField(child=serializers.FloatField(), required=False)
    occasions = serializers.DictField(child=serializers.FloatField(), required=False)
    color_harmony = serializers.FloatField(required=False)
    style_consistency = serializers.FloatField(required=False)
    brand_diversity = serializers.FloatField(required=False)
    favorite_usage = serializers.FloatField(required=False)
    weather_appropriate = serializers.FloatField(required=False)
    learning_rate = serializers.FloatField()
    confidence_threshold = serializers.FloatField()
    last_updated = serializers.DateTimeField()


class FeedbackStatsSerializer(serializers.Serializer):
    """Serializer for feedback statistics"""
    
    total_feedback = serializers.IntegerField()
    likes = serializers.IntegerField()
    dislikes = serializers.IntegerField()
    ratings_count = serializers.IntegerField()
    average_rating = serializers.FloatField(allow_null=True)
    like_percentage = serializers.FloatField()
    most_liked_occasion = serializers.CharField(allow_null=True)
    most_disliked_occasion = serializers.CharField(allow_null=True)
    feedback_trend = serializers.ListField(child=serializers.DictField(), required=False)
