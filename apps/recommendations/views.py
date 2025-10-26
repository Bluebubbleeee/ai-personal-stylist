"""
Recommendations views for AI-Powered Personal Stylist & Wardrobe Manager
"""

import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views import View
from django.utils.decorators import method_decorator
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta

from .models import OutfitSuggestion, RecommendationSession, WeatherCache, StyleVector
from apps.wardrobe.models import ClothingItem
from .ai_outfit_service import AIOutfitService
from apps.common.models import AuditLog

logger = logging.getLogger(__name__)


def generate_recommendations_api(request):
    """API endpoint for generating recommendations"""
    return JsonResponse({'message': 'API endpoint for generating recommendations'})


def weather_api(request):
    """API endpoint for weather data"""
    return JsonResponse({'message': 'Weather API endpoint'})


@method_decorator([login_required, csrf_protect], name='dispatch')
class StyleMeView(View):
    """Main Style Me recommendation view"""
    
    def get(self, request):
        """Display Style Me interface"""
        # Get user's recent recommendations (only active/successful ones)
        recent_suggestions = OutfitSuggestion.objects.filter(
            user=request.user,
            is_active=True
        ).order_by('-created_at')[:6]
        
        # Get wardrobe stats
        wardrobe_items = ClothingItem.active_objects.for_user(request.user)
        wardrobe_stats = {
            'total_items': wardrobe_items.count(),
            'categories': {}
        }
        
        for category, label in ClothingItem.CATEGORY_CHOICES:
            count = wardrobe_items.filter(category=category).count()
            if count > 0:
                wardrobe_stats['categories'][category] = {'label': label, 'count': count}
        
        context = {
            'recent_suggestions': recent_suggestions,
            'wardrobe_stats': wardrobe_stats,
            'occasion_choices': [
                'casual', 'work', 'formal', 'party', 'date', 'travel',
                'sports', 'shopping', 'meeting', 'dinner', 'weekend'
            ]
        }
        
        return render(request, 'recommendations/style_me.html', context)
    
    def post(self, request):
        """Generate outfit recommendations based on user input"""
        try:
            # Get form data
            occasion = request.POST.get('occasion', 'casual')
            custom_prompt = request.POST.get('custom_prompt', '')
            location = request.POST.get('location', '')
            weather_consideration = request.POST.get('weather_consideration', 'true') == 'true'
            
            # Create recommendation session
            session = RecommendationSession.objects.create(
                user=request.user,
                original_prompt=f"{occasion}: {custom_prompt}" if custom_prompt else occasion,
                location=location,
                weather_data={}  # Will be populated if weather is considered
            )
            
            # Generate recommendations using AI service
            ai_service = AIOutfitService()
            
            # Get weather data if weather consideration is enabled
            weather_data = None
            if weather_consideration and session.location:
                # Use the existing weather API endpoint
                try:
                    import requests
                    from django.conf import settings
                    
                    # Parse coordinates if provided as "lat,lon"
                    if ',' in session.location:
                        lat, lon = session.location.split(',')
                        weather_url = f"/api/weather/?lat={lat}&lon={lon}"
                    else:
                        # If it's a city name, we'd need to geocode it first
                        # For now, skip weather if not coordinates
                        weather_data = None
                    
                    if weather_url:
                        # Make internal request to our weather API
                        from django.test import Client
                        client = Client()
                        response = client.get(weather_url)
                        
                        if response.status_code == 200:
                            weather_data = response.json()
                            session.weather_data = weather_data
                            session.save()
                        else:
                            logger.warning(f"Weather API returned status {response.status_code}")
                            
                except Exception as e:
                    logger.error(f"Error fetching weather data: {str(e)}")
                    weather_data = None
            
            recommendations = ai_service.generate_outfit_recommendations(
                request.user, 
                session, 
                weather_data, 
                occasion, 
                custom_prompt
            )
            
            if recommendations:
                # Check if any recommendations are error suggestions
                error_suggestions = [rec for rec in recommendations if not rec.is_active and "AI Recommendation Error" in rec.ai_rationale]
                if error_suggestions:
                    error_message = error_suggestions[0].ai_rationale.replace("AI Recommendation Error: ", "")
                    messages.warning(request, f'Our AI stylist couldn\'t create outfit recommendations: {error_message}')
                else:
                    messages.success(request, f'Generated {len(recommendations)} AI-powered outfit suggestions for you!')
            else:
                # AI couldn't generate recommendations - show helpful message
                messages.info(request, 'Our AI stylist is working on your outfit recommendations. This might take a moment, or you might want to add more items to your wardrobe for better suggestions.')
            
            # Filter out error suggestions from display
            display_recommendations = [rec for rec in recommendations if rec.is_active]
            
            context = {
                'recommendations': display_recommendations,
                'session': session,
                'wardrobe_stats': self.get_wardrobe_stats(request.user),
                'occasion_choices': [
                    'casual', 'work', 'formal', 'party', 'date', 'travel',
                    'sports', 'shopping', 'meeting', 'dinner', 'weekend'
                ]
            }
            
            return render(request, 'recommendations/style_me.html', context)
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            messages.error(request, 'An error occurred while generating recommendations. Please try again.')
            return self.get(request)
    
    
    
    def get_wardrobe_stats(self, user):
        """Get wardrobe statistics for display"""
        wardrobe_items = ClothingItem.active_objects.for_user(user)
        stats = {
            'total_items': wardrobe_items.count(),
            'categories': {}
        }
        
        for category, label in ClothingItem.CATEGORY_CHOICES:
            count = wardrobe_items.filter(category=category).count()
            if count > 0:
                stats['categories'][category] = {'label': label, 'count': count}
        
        return stats


class SuggestionDetailView(View):
    """Display full details of a specific outfit suggestion"""
    
    def get(self, request, suggestion_id):
        try:
            suggestion = get_object_or_404(OutfitSuggestion, 
                                         suggestion_id=suggestion_id, 
                                         user=request.user)
            
            context = {
                'suggestion': suggestion,
                'wardrobe_stats': self.get_wardrobe_stats(request.user),
            }
            
            return render(request, 'recommendations/suggestion_detail.html', context)
            
        except Exception as e:
            logger.error(f"Error displaying suggestion details: {str(e)}")
            messages.error(request, 'Unable to load suggestion details.')
            return redirect('style_me')
    
    def get_wardrobe_stats(self, user):
        """Get wardrobe statistics for display"""
        wardrobe_items = ClothingItem.active_objects.for_user(user)
        stats = {
            'total_items': wardrobe_items.count(),
            'categories': {}
        }
        
        # Category breakdown
        category_choices = ClothingItem.CATEGORY_CHOICES
        for category, label in category_choices:
            count = wardrobe_items.filter(category=category).count()
            if count > 0:
                stats['categories'][category] = {'label': label, 'count': count}
        
        return stats

