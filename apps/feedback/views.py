"""
Feedback views for AI-Powered Personal Stylist & Wardrobe Manager
"""

import json
import logging
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.db.models import Avg

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import OutfitFeedback
from apps.recommendations.models import OutfitSuggestion, StyleVector
from apps.common.models import AuditLog

logger = logging.getLogger(__name__)


@login_required
@csrf_protect
def submit_feedback(request):
    """Submit feedback for an outfit recommendation"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
            
            suggestion_id = data.get('suggestion_id')
            feedback_type = data.get('feedback_type')  # 'like', 'dislike', 'rating'
            rating = data.get('rating')  # 1-5 stars
            comments = data.get('comments', '')
            
            # Validate input
            suggestion = get_object_or_404(OutfitSuggestion, 
                                         suggestion_id=suggestion_id, 
                                         user=request.user)
            
            if feedback_type not in ['like', 'dislike', 'rating']:
                return JsonResponse({'success': False, 'error': 'Invalid feedback type'})
            
            # Create or update feedback
            feedback, created = OutfitFeedback.objects.get_or_create(
                user=request.user,
                suggestion=suggestion,
                defaults={
                    'feedback_type': feedback_type,
                    'rating': rating,
                    'comments': comments
                }
            )
            
            if not created:
                # Update existing feedback
                feedback.feedback_type = feedback_type
                feedback.rating = rating
                feedback.comments = comments
                feedback.save()
            
            # Update user's style preferences using EMA
            update_style_preferences(request.user, suggestion, feedback)
            
            return JsonResponse({
                'success': True,
                'message': 'Thank you for your feedback!',
                'feedback_id': str(feedback.feedback_id)
            })
            
        except Exception as e:
            logger.error(f"Error submitting feedback: {str(e)}")
            return JsonResponse({'success': False, 'error': 'Failed to submit feedback'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def update_style_preferences(user, suggestion, feedback):
    """Update user's style preferences using Exponential Moving Average (EMA)"""
    try:
        # Get or create user's style vector
        style_vector, created = StyleVector.objects.get_or_create(
            user=user,
            defaults={
                'preferences': {},
                'learning_rate': 0.1,
                'confidence_threshold': 0.7
            }
        )
        
        current_prefs = style_vector.preferences if style_vector.preferences else {}
        learning_rate = style_vector.learning_rate
        
        # Determine feedback weight
        if feedback.feedback_type == 'like':
            feedback_weight = 1.0
        elif feedback.feedback_type == 'dislike':
            feedback_weight = -1.0
        elif feedback.feedback_type == 'rating' and feedback.rating:
            # Convert 1-5 rating to -1 to 1 scale
            feedback_weight = (feedback.rating - 3) / 2.0
        else:
            feedback_weight = 0.0
        
        # Update color preferences
        colors = [item.color for item in suggestion.items.all() if item.color]
        for color in colors:
            color_key = f"color_{color}"
            if color_key in current_prefs:
                current_prefs[color_key] = (1 - learning_rate) * current_prefs[color_key] + learning_rate * feedback_weight
            else:
                current_prefs[color_key] = learning_rate * feedback_weight
            
            # Clamp values between -1 and 1
            current_prefs[color_key] = max(-1.0, min(1.0, current_prefs[color_key]))
        
        # Update occasion preferences
        occasion_key = f"occasion_{suggestion.occasion}"
        if occasion_key in current_prefs:
            current_prefs[occasion_key] = (1 - learning_rate) * current_prefs[occasion_key] + learning_rate * feedback_weight
        else:
            current_prefs[occasion_key] = learning_rate * feedback_weight
        
        current_prefs[occasion_key] = max(-1.0, min(1.0, current_prefs[occasion_key]))
        
        # Save updated preferences
        style_vector.preferences = current_prefs
        style_vector.save()
        
        logger.info(f"Updated style preferences for user {user.user_id}")
        
    except Exception as e:
        logger.error(f"Error updating style preferences: {str(e)}")


# API Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_feedback_api(request):
    """API endpoint for submitting feedback"""
    try:
        suggestion_id = request.data.get('suggestion_id')
        feedback_type = request.data.get('feedback_type')
        rating = request.data.get('rating')
        comments = request.data.get('comments', '')
        
        suggestion = get_object_or_404(OutfitSuggestion, 
                                     suggestion_id=suggestion_id, 
                                     user=request.user)
        
        if feedback_type not in ['like', 'dislike', 'rating']:
            return Response({'error': 'Invalid feedback type'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or update feedback
        feedback, created = OutfitFeedback.objects.get_or_create(
            user=request.user,
            suggestion=suggestion,
            defaults={
                'feedback_type': feedback_type,
                'rating': rating,
                'comments': comments
            }
        )
        
        if not created:
            feedback.feedback_type = feedback_type
            feedback.rating = rating
            feedback.comments = comments
            feedback.save()
        
        # Update style preferences
        update_style_preferences(request.user, suggestion, feedback)
        
        return Response({
            'success': True,
            'message': 'Feedback submitted successfully'
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in feedback API: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to submit feedback'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)