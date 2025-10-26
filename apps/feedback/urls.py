"""
Feedback URLs for AI-Powered Personal Stylist & Wardrobe Manager
"""

from django.urls import path, include
from . import views

# Web URLs (for regular pages)
web_urlpatterns = [
    path('submit/', views.submit_feedback, name='submit_feedback'),
    path('history/', views.feedback_history, name='feedback_history'),
]

# API URLs (for AJAX/mobile/API access)
api_urlpatterns = [
    path('submit/', views.submit_feedback_api, name='api_submit_feedback'),
    path('preferences/', views.style_preferences_api, name='api_style_preferences'),
]

urlpatterns = [
    # Web interface URLs
    path('', include(web_urlpatterns)),
    
    # API URLs
    path('api/', include(api_urlpatterns)),
]
