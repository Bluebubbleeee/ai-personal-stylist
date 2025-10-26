"""
Recommendations serializers for AI-Powered Personal Stylist & Wardrobe Manager
"""

from rest_framework import serializers
from .models import OutfitSuggestion, RecommendationSession, StyleVector, WeatherCache
from apps.wardrobe.serializers import ClothingItemSerializer


class StyleVectorSerializer(serializers.ModelSerializer):
    """Serializer for user style preferences"""
    
    class Meta:
        model = StyleVector
        fields = ['preferences', 'learning_rate', 'confidence_threshold', 'updated_at']
        read_only_fields = ['updated_at']


class OutfitSuggestionSerializer(serializers.ModelSerializer):
    """Serializer for outfit suggestions"""
    
    items = ClothingItemSerializer(many=True, read_only=True)
    confidence_score_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = OutfitSuggestion
        fields = [
            'suggestion_id', 'occasion', 'ai_rationale', 'confidence_score',
            'confidence_score_percentage', 'weather_context', 'items', 'created_at'
        ]
        read_only_fields = ['suggestion_id', 'created_at']
    
    def get_confidence_score_percentage(self, obj):
        """Get confidence score as percentage"""
        return round(obj.confidence_score * 100) if obj.confidence_score else 0


class RecommendationSessionSerializer(serializers.ModelSerializer):
    """Serializer for recommendation sessions"""
    
    suggestions = OutfitSuggestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = RecommendationSession
        fields = [
            'session_id', 'occasion', 'custom_prompt', 'location',
            'weather_consideration', 'weather_data', 'suggestions', 'created_at'
        ]
        read_only_fields = ['session_id', 'weather_data', 'created_at']


class WeatherCacheSerializer(serializers.ModelSerializer):
    """Serializer for weather cache data"""
    
    class Meta:
        model = WeatherCache
        fields = ['location', 'weather_data', 'cached_at', 'expires_at']
        read_only_fields = ['cached_at', 'expires_at']


class RecommendationRequestSerializer(serializers.Serializer):
    """Serializer for recommendation API requests"""
    
    occasion = serializers.ChoiceField(
        choices=[
            ('casual', 'Casual'),
            ('work', 'Work'),
            ('formal', 'Formal'),
            ('party', 'Party'),
            ('date', 'Date'),
            ('travel', 'Travel'),
            ('sports', 'Sports'),
            ('shopping', 'Shopping'),
            ('meeting', 'Meeting'),
            ('dinner', 'Dinner'),
            ('weekend', 'Weekend'),
        ],
        default='casual'
    )
    custom_prompt = serializers.CharField(max_length=500, required=False, allow_blank=True)
    location = serializers.CharField(max_length=100, required=False, allow_blank=True)
    weather_consideration = serializers.BooleanField(default=True)
    
    def validate_custom_prompt(self, value):
        """Validate custom prompt"""
        if value and len(value.strip()) < 5:
            raise serializers.ValidationError("Custom prompt should be at least 5 characters long if provided.")
        return value.strip() if value else ""
