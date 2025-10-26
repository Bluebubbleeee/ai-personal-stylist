"""
Wardrobe models for AI-Powered Personal Stylist & Wardrobe Manager
"""

import uuid
import os
from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.conf import settings
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile


def clothing_image_path(instance, filename):
    """Generate file path for clothing item images"""
    ext = filename.split('.')[-1]
    filename = f"{instance.item_id}.{ext}"
    return os.path.join('clothing', str(instance.user.user_id), filename)


def clothing_thumbnail_path(instance, filename):
    """Generate file path for clothing item thumbnails"""
    ext = filename.split('.')[-1]
    filename = f"{instance.item_id}_thumb.{ext}"
    return os.path.join('clothing', 'thumbnails', str(instance.user.user_id), filename)


class ClothingItem(models.Model):
    """
    Model representing a clothing item in user's wardrobe
    Based on the database schema from steps.txt
    """
    
    CATEGORY_CHOICES = [
        ('tops', 'Tops'),
        ('bottoms', 'Bottoms'),
        ('dresses', 'Dresses'),
        ('outerwear', 'Outerwear'),
        ('shoes', 'Shoes'),
        ('accessories', 'Accessories'),
        ('underwear', 'Underwear'),
        ('activewear', 'Activewear'),
        ('formal', 'Formal'),
        ('sleepwear', 'Sleepwear'),
        ('other', 'Other'),
    ]
    
    COLOR_CHOICES = [
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('orange', 'Orange'),
        ('purple', 'Purple'),
        ('pink', 'Pink'),
        ('brown', 'Brown'),
        ('black', 'Black'),
        ('white', 'White'),
        ('grey', 'Grey'),
        ('beige', 'Beige'),
        ('navy', 'Navy'),
        ('maroon', 'Maroon'),
        ('teal', 'Teal'),
        ('olive', 'Olive'),
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('multicolor', 'Multicolor'),
        ('other', 'Other'),
    ]
    
    SEASON_CHOICES = [
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('fall', 'Fall'),
        ('winter', 'Winter'),
        ('all_season', 'All Season'),
    ]
    
    item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='clothing_items'
    )
    
    # Basic information
    name = models.CharField(max_length=100, help_text="User-defined name for the item")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    subcategory = models.CharField(max_length=50, blank=True, help_text="More specific category")
    color = models.CharField(max_length=50, choices=COLOR_CHOICES, default='other')
    secondary_color = models.CharField(max_length=50, choices=COLOR_CHOICES, blank=True)
    
    # Images
    image = models.ImageField(
        upload_to=clothing_image_path,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])],
        help_text="Main image of the clothing item"
    )
    thumbnail = models.ImageField(
        upload_to=clothing_thumbnail_path,
        blank=True,
        help_text="Thumbnail version of the image"
    )
    
    # Metadata from computer vision
    cv_confidence = models.FloatField(
        null=True, 
        blank=True, 
        help_text="Confidence score from computer vision classification"
    )
    cv_metadata = models.JSONField(
        default=dict,
        help_text="Additional metadata from computer vision analysis"
    )
    cv_description = models.TextField(
        blank=True,
        help_text="Hidden AI-generated concise description for better recommendations"
    )
    
    # Usage and preferences
    season = models.CharField(max_length=20, choices=SEASON_CHOICES, default='all_season')
    brand = models.CharField(max_length=100, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Status and tracking
    is_favorite = models.BooleanField(default=False)
    wear_count = models.IntegerField(default=0, help_text="Number of times worn")
    last_worn = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True, help_text="Whether item is active in wardrobe")
    is_dirty = models.BooleanField(default=False, help_text="Whether item needs washing")
    
    # Soft delete
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'clothing_items'
        verbose_name = 'Clothing Item'
        verbose_name_plural = 'Clothing Items'
        indexes = [
            models.Index(fields=['user', 'category']),
            models.Index(fields=['user', 'color']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['deleted_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.category})"
    
    def save(self, *args, **kwargs):
        """Override save to create thumbnail"""
        # Save the model first to get the file paths
        super().save(*args, **kwargs)
        
        # Create thumbnail if image exists and thumbnail doesn't
        if self.image and not self.thumbnail:
            self.create_thumbnail()
    
    def create_thumbnail(self):
        """Create a thumbnail for the clothing item image"""
        if not self.image:
            return
        
        try:
            # Open the image
            img = Image.open(self.image.path)
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Create thumbnail
            thumbnail_size = getattr(settings, 'THUMBNAIL_SIZE', (300, 300))
            img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
            
            # Save thumbnail
            thumb_io = BytesIO()
            img.save(thumb_io, format='JPEG', quality=85)
            
            # Create InMemoryUploadedFile
            thumbnail_file = InMemoryUploadedFile(
                thumb_io,
                None,
                f"{self.item_id}_thumb.jpg",
                'image/jpeg',
                thumb_io.tell(),
                None
            )
            
            # Save thumbnail to the model
            self.thumbnail.save(
                f"{self.item_id}_thumb.jpg",
                thumbnail_file,
                save=True
            )
            
        except Exception as e:
            print(f"Error creating thumbnail for {self.item_id}: {e}")
    
    def soft_delete(self):
        """Soft delete the item"""
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=['deleted_at', 'is_active'])
    
    def restore(self):
        """Restore a soft-deleted item"""
        self.deleted_at = None
        self.is_active = True
        self.save(update_fields=['deleted_at', 'is_active'])
    
    @property
    def is_deleted(self):
        """Check if item is soft deleted"""
        return self.deleted_at is not None
    
    def increment_wear_count(self):
        """Increment wear count and update last worn date"""
        self.wear_count += 1
        self.last_worn = timezone.now().date()
        self.save(update_fields=['wear_count', 'last_worn'])


class Tag(models.Model):
    """
    Model representing tags for clothing items
    Based on the database schema from steps.txt
    """
    tag_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(
        ClothingItem,
        on_delete=models.CASCADE,
        related_name='tags'
    )
    tag = models.CharField(max_length=50, help_text="Tag name (normalized)")
    
    # Tag metadata
    source = models.CharField(
        max_length=20,
        choices=[
            ('user', 'User Added'),
            ('cv', 'Computer Vision'),
            ('system', 'System Generated'),
        ],
        default='user'
    )
    confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="Confidence score if generated by CV"
    )
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'tags'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        unique_together = [['item', 'tag']]  # Prevent duplicate tags on same item
        indexes = [
            models.Index(fields=['item']),
            models.Index(fields=['tag']),
            models.Index(fields=['source']),
        ]
    
    def __str__(self):
        return f"{self.tag} ({self.item.name})"
    
    def save(self, *args, **kwargs):
        """Override save to normalize tag name"""
        self.tag = self.tag.lower().strip()
        super().save(*args, **kwargs)


class CanonicalTag(models.Model):
    """
    Model for maintaining canonical tag vocabulary
    """
    name = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=50, blank=True)
    synonyms = models.JSONField(
        default=list,
        help_text="List of synonyms for this canonical tag"
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'canonical_tags'
        verbose_name = 'Canonical Tag'
        verbose_name_plural = 'Canonical Tags'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @classmethod
    def normalize_tag(cls, tag_name):
        """
        Normalize a tag name to its canonical form
        Returns the canonical form or the original if no match found
        """
        tag_name = tag_name.lower().strip()
        
        # Try exact match first
        try:
            canonical = cls.objects.get(name=tag_name, is_active=True)
            return canonical.name
        except cls.DoesNotExist:
            pass
        
        # Try synonym match
        for canonical in cls.objects.filter(is_active=True):
            if tag_name in [synonym.lower() for synonym in canonical.synonyms]:
                return canonical.name
        
        # Return original if no match
        return tag_name


class WardrobeManager(models.Manager):
    """Custom manager for active (non-deleted) clothing items"""
    
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)
    
    def for_user(self, user):
        """Get active clothing items for a specific user"""
        return self.filter(user=user, is_active=True)
    
    def by_category(self, user, category):
        """Get items by category for a user"""
        return self.for_user(user).filter(category=category)
    
    def by_color(self, user, color):
        """Get items by color for a user"""
        return self.for_user(user).filter(
            models.Q(color=color) | models.Q(secondary_color=color)
        )
    
    def search(self, user, query):
        """Search items by name, category, or tags"""
        return self.for_user(user).filter(
            models.Q(name__icontains=query) |
            models.Q(category__icontains=query) |
            models.Q(subcategory__icontains=query) |
            models.Q(tags__tag__icontains=query)
        ).distinct()


# Add the custom manager to ClothingItem
ClothingItem.add_to_class('active_objects', WardrobeManager())