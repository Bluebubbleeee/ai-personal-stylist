"""
Wardrobe serializers for AI-Powered Personal Stylist & Wardrobe Manager
"""

from rest_framework import serializers
from django.db.models import Q
from .models import ClothingItem, Tag, CanonicalTag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for clothing item tags"""
    
    class Meta:
        model = Tag
        fields = ['tag_id', 'tag', 'source', 'confidence', 'created_at']
        read_only_fields = ['tag_id', 'created_at']


class ClothingItemSerializer(serializers.ModelSerializer):
    """Serializer for clothing items"""
    
    tags = TagSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ClothingItem
        fields = [
            'item_id', 'name', 'category', 'subcategory', 'color', 'secondary_color',
            'season', 'brand', 'purchase_date', 'price', 'is_favorite', 'wear_count',
            'last_worn', 'image_url', 'thumbnail_url', 'tags', 'cv_confidence',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'item_id', 'wear_count', 'last_worn', 'cv_confidence', 'created_at', 'updated_at'
        ]
    
    def get_image_url(self, obj):
        """Get full image URL"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_thumbnail_url(self, obj):
        """Get thumbnail image URL"""
        if obj.thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None
    
    def validate_image(self, value):
        """Validate uploaded image"""
        if value:
            # Check file size (10MB max)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("Image file too large. Maximum size is 10MB.")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/webp']
            if hasattr(value, 'content_type') and value.content_type not in allowed_types:
                raise serializers.ValidationError("Unsupported image format. Please use JPEG, PNG, or WebP.")
        
        return value


class CanonicalTagSerializer(serializers.ModelSerializer):
    """Serializer for canonical tags"""
    
    class Meta:
        model = CanonicalTag
        fields = ['name', 'category', 'synonyms', 'description', 'is_active']
        read_only_fields = ['created_at', 'updated_at']


class ClothingItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating clothing items with tags"""
    
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        help_text="List of tags to add to this item"
    )
    
    class Meta:
        model = ClothingItem
        fields = [
            'name', 'category', 'subcategory', 'color', 'secondary_color',
            'season', 'brand', 'purchase_date', 'price', 'image', 'tags'
        ]
    
    def create(self, validated_data):
        """Create clothing item with tags"""
        tags_data = validated_data.pop('tags', [])
        item = ClothingItem.objects.create(**validated_data)
        
        # Add tags
        for tag_name in tags_data:
            normalized_tag = CanonicalTag.normalize_tag(tag_name)
            Tag.objects.get_or_create(
                item=item,
                tag=normalized_tag,
                defaults={'source': 'user'}
            )
        
        return item


class WardrobeStatsSerializer(serializers.Serializer):
    """Serializer for wardrobe statistics"""
    
    total_items = serializers.IntegerField()
    favorite_items = serializers.IntegerField()
    categories = serializers.DictField()
    colors = serializers.DictField()
    recent_additions = serializers.IntegerField()
    most_worn = serializers.ListField()
    least_worn = serializers.ListField()
    
    def to_representation(self, instance):
        """Custom representation for wardrobe stats"""
        user = instance
        items = ClothingItem.active_objects.for_user(user)
        
        # Category breakdown
        categories = {}
        for category, label in ClothingItem.CATEGORY_CHOICES:
            count = items.filter(category=category).count()
            if count > 0:
                categories[category] = {'label': label, 'count': count}
        
        # Color breakdown
        colors = {}
        for color, label in ClothingItem.COLOR_CHOICES:
            count = items.filter(Q(color=color) | Q(secondary_color=color)).count()
            if count > 0:
                colors[color] = {'label': label, 'count': count}
        
        # Recent additions (last 7 days)
        from django.utils import timezone
        from datetime import timedelta
        recent_date = timezone.now() - timedelta(days=7)
        recent_additions = items.filter(created_at__gte=recent_date).count()
        
        # Most and least worn items
        most_worn = items.exclude(wear_count=0).order_by('-wear_count')[:5]
        least_worn = items.filter(wear_count=0)[:5]
        
        return {
            'total_items': items.count(),
            'favorite_items': items.filter(is_favorite=True).count(),
            'categories': categories,
            'colors': colors,
            'recent_additions': recent_additions,
            'most_worn': [{'name': item.name, 'wear_count': item.wear_count} for item in most_worn],
            'least_worn': [{'name': item.name, 'category': item.get_category_display()} for item in least_worn],
        }
