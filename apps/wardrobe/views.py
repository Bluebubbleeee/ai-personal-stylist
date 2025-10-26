"""
Wardrobe views for AI-Powered Personal Stylist & Wardrobe Manager
"""

import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from django.views import View
from django.utils.decorators import method_decorator
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from PIL import Image
import os

from .models import ClothingItem, Tag, CanonicalTag
from apps.common.models import AuditLog
from .computer_vision_api import analyze_image_openai_api, test_openai_api

logger = logging.getLogger(__name__)


@method_decorator([login_required, csrf_protect], name='dispatch')
class WardrobeView(View):
    """Main wardrobe view with all clothing items"""
    
    def get(self, request):
        # Get search and filter parameters
        search_query = request.GET.get('q', '')
        category_filter = request.GET.get('category', '')
        color_filter = request.GET.get('color', '')
        favorites_only = request.GET.get('favorites', '') == 'true'
        
        # Base queryset
        items = ClothingItem.active_objects.for_user(request.user)
        
        # Apply search
        if search_query:
            items = items.filter(
                Q(name__icontains=search_query) |
                Q(category__icontains=search_query) |
                Q(subcategory__icontains=search_query) |
                Q(brand__icontains=search_query) |
                Q(tags__tag__icontains=search_query)
            ).distinct()
        
        # Apply filters
        if category_filter:
            items = items.filter(category=category_filter)
        
        if color_filter:
            items = items.filter(Q(color=color_filter) | Q(secondary_color=color_filter))
        
        # Apply favorites filter
        if favorites_only:
            items = items.filter(is_favorite=True)
        
        # Pagination
        paginator = Paginator(items, 20)
        page_number = request.GET.get('page')
        page_items = paginator.get_page(page_number)
        
        # Get filter choices for dropdowns
        categories = ClothingItem.CATEGORY_CHOICES
        colors = ClothingItem.COLOR_CHOICES
        
        context = {
            'items': page_items,
            'search_query': search_query,
            'category_filter': category_filter,
            'color_filter': color_filter,
            'favorites_only': favorites_only,
            'categories': categories,
            'colors': colors,
            'total_items': items.count(),
        }
        
        return render(request, 'wardrobe/wardrobe.html', context)


@method_decorator([login_required, csrf_protect], name='dispatch')
class UploadView(View):
    """Clothing item upload view"""
    
    def get(self, request):
        categories = ClothingItem.CATEGORY_CHOICES
        colors = ClothingItem.COLOR_CHOICES
        seasons = ClothingItem.SEASON_CHOICES
        
        context = {
            'categories': categories,
            'colors': colors,
            'seasons': seasons,
        }
        
        return render(request, 'wardrobe/upload.html', context)
    
    def post(self, request):
        try:
            # Handle file upload
            uploaded_file = request.FILES.get('image')
            if not uploaded_file:
                messages.error(request, 'Please select an image to upload.')
                return redirect('wardrobe_upload')
            
            # Validate file
            if not self.validate_image(uploaded_file):
                messages.error(request, 'Please upload a valid image file (JPEG, PNG, WebP) under 10MB.')
                return redirect('wardrobe_upload')
            
            # Create clothing item
            item = ClothingItem(
                user=request.user,
                name=request.POST.get('name', 'New Item'),
                category=request.POST.get('category', 'other'),
                subcategory=request.POST.get('subcategory', ''),
                color=request.POST.get('color', 'other'),
                secondary_color=request.POST.get('secondary_color', ''),
                season=request.POST.get('season', 'all_season'),
                brand=request.POST.get('brand', ''),
                image=uploaded_file,
                cv_description=request.POST.get('cv_description', '').strip()
            )
            
            item.save()
            
            # Add manual tags if provided
            manual_tags = request.POST.get('tags', '').strip()
            if manual_tags:
                tag_names = [tag.strip() for tag in manual_tags.split(',') if tag.strip()]
                for tag_name in tag_names:
                    normalized_tag = CanonicalTag.normalize_tag(tag_name)
                    Tag.objects.get_or_create(
                        item=item,
                        tag=normalized_tag,
                        defaults={'source': 'user'}
                    )
            
            # Run computer vision analysis
            from .cv_service import analyze_clothing_item
            cv_results = analyze_clothing_item(item)
            
            messages.success(request, f'"{item.name}" has been added to your wardrobe!')
            return redirect('wardrobe')
            
        except Exception as e:
            logger.error(f"Error uploading clothing item: {str(e)}")
            messages.error(request, 'An error occurred while uploading your item. Please try again.')
            return redirect('wardrobe_upload')
    
    def validate_image(self, uploaded_file):
        """Validate uploaded image file"""
        # Check file size (10MB max)
        if uploaded_file.size > 10 * 1024 * 1024:
            return False
        
        # Check file type
        allowed_types = ['image/jpeg', 'image/png', 'image/webp']
        if uploaded_file.content_type not in allowed_types:
            return False
        
        try:
            with Image.open(uploaded_file) as img:
                img.verify()
            uploaded_file.seek(0)
            return True
        except Exception:
            return False
    


@method_decorator([login_required, csrf_protect], name='dispatch')
class ItemDetailView(View):
    """Individual clothing item detail view"""
    
    def get(self, request, item_id):
        item = get_object_or_404(ClothingItem, item_id=item_id, user=request.user)
        tags = item.tags.all().order_by('tag')
        
        context = {
            'item': item,
            'tags': tags,
            'categories': ClothingItem.CATEGORY_CHOICES,
            'colors': ClothingItem.COLOR_CHOICES,
            'seasons': ClothingItem.SEASON_CHOICES,
        }
        
        return render(request, 'wardrobe/item_detail.html', context)


@login_required
def delete_item_view(request, item_id):
    """Delete clothing item (soft delete)"""
    item = get_object_or_404(ClothingItem, item_id=item_id, user=request.user)
    
    if request.method == 'POST':
        item_name = item.name
        item.soft_delete()
        messages.success(request, f'"{item_name}" has been removed from your wardrobe.')
        return redirect('wardrobe')
    
    return render(request, 'wardrobe/confirm_delete.html', {'item': item})


@login_required
def toggle_favorite(request, item_id):
    """Toggle favorite status of clothing item"""
    item = get_object_or_404(ClothingItem, item_id=item_id, user=request.user)
    
    item.is_favorite = not item.is_favorite
    item.save(update_fields=['is_favorite'])
    
    return JsonResponse({
        'success': True,
        'is_favorite': item.is_favorite,
        'message': 'Added to favorites' if item.is_favorite else 'Removed from favorites'
    })


@method_decorator([login_required, csrf_protect], name='dispatch')
class EditItemView(View):
    """Edit clothing item view"""
    
    def get(self, request, item_id):
        item = get_object_or_404(ClothingItem, item_id=item_id, user=request.user)
        
        categories = ClothingItem.CATEGORY_CHOICES
        colors = ClothingItem.COLOR_CHOICES
        seasons = ClothingItem.SEASON_CHOICES
        
        context = {
            'item': item,
            'categories': categories,
            'colors': colors,
            'seasons': seasons,
        }
        
        return render(request, 'wardrobe/edit_item.html', context)
    
    def post(self, request, item_id):
        item = get_object_or_404(ClothingItem, item_id=item_id, user=request.user)
        
        try:
            # Update item fields
            item.name = request.POST.get('name', item.name)
            item.category = request.POST.get('category', item.category)
            item.subcategory = request.POST.get('subcategory', item.subcategory)
            item.color = request.POST.get('color', item.color)
            item.secondary_color = request.POST.get('secondary_color', item.secondary_color)
            item.season = request.POST.get('season', item.season)
            item.brand = request.POST.get('brand', item.brand)
            item.cv_description = request.POST.get('cv_description', item.cv_description)
            
            item.save()
            
            # Update tags
            manual_tags = request.POST.get('tags', '').strip()
            if manual_tags:
                # Clear existing user tags
                item.tags.filter(source='user').delete()
                
                # Add new tags
                tag_names = [tag.strip() for tag in manual_tags.split(',') if tag.strip()]
                for tag_name in tag_names:
                    normalized_tag = CanonicalTag.normalize_tag(tag_name)
                    Tag.objects.get_or_create(
                        item=item,
                        tag=normalized_tag,
                        defaults={'source': 'user'}
                    )
            
            messages.success(request, f'"{item.name}" has been updated successfully!')
            return redirect('item_detail', item_id=item.item_id)
            
        except Exception as e:
            logger.error(f"Error updating item {item_id}: {str(e)}")
            messages.error(request, 'An error occurred while updating the item.')
            return redirect('edit_item', item_id=item.item_id)


@login_required
def search_suggestions(request):
    """Get search suggestions for autocomplete"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    items = ClothingItem.active_objects.for_user(request.user)
    suggestions = set()
    
    # Add matching item names
    matching_items = items.filter(name__icontains=query)[:5]
    for item in matching_items:
        suggestions.add(item.name)
    
    # Add matching tags
    matching_tags = Tag.objects.filter(
        item__user=request.user,
        tag__icontains=query
    ).distinct()[:5]
    for tag in matching_tags:
        suggestions.add(tag.tag)
    
    return JsonResponse({'suggestions': sorted(list(suggestions))[:10]})


# API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wardrobe_api(request):
    """API endpoint to get user's wardrobe items"""
    items = ClothingItem.active_objects.for_user(request.user)
    
    # Apply search and filters
    search_query = request.GET.get('q')
    if search_query:
        items = items.filter(
            Q(name__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(tags__tag__icontains=search_query)
        ).distinct()
    
    category = request.GET.get('category')
    if category:
        items = items.filter(category=category)
    
    color = request.GET.get('color')
    if color:
        items = items.filter(Q(color=color) | Q(secondary_color=color))
    
    from .serializers import ClothingItemSerializer
    serializer = ClothingItemSerializer(items, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_item_api(request):
    """API endpoint for uploading clothing items"""
    from .serializers import ClothingItemCreateSerializer
    serializer = ClothingItemCreateSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        item = serializer.save(user=request.user)
        from .serializers import ClothingItemSerializer
        return Response(ClothingItemSerializer(item, context={'request': request}).data, 
                       status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def item_detail_api(request, item_id):
    """API endpoint for individual clothing item operations"""
    item = get_object_or_404(ClothingItem, item_id=item_id, user=request.user)
    
    if request.method == 'GET':
        from .serializers import ClothingItemSerializer
        serializer = ClothingItemSerializer(item, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        from .serializers import ClothingItemSerializer
        serializer = ClothingItemSerializer(item, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        item.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wardrobe_stats_api(request):
    """API endpoint for wardrobe statistics"""
    from .serializers import WardrobeStatsSerializer
    serializer = WardrobeStatsSerializer(request.user)
    return Response(serializer.data)