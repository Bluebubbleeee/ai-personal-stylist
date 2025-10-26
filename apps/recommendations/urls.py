"""
Recommendations URLs for AI-Powered Personal Stylist & Wardrobe Manager
"""

from django.urls import path, include
from . import views
from . import weather_api

# Web URLs (for regular pages)
web_urlpatterns = [
    path('', views.StyleMeView.as_view(), name='style_me'),
    path('suggestion/<uuid:suggestion_id>/', views.SuggestionDetailView.as_view(), name='suggestion_detail'),
]

# API URLs (for AJAX/mobile/API access)
api_urlpatterns = [
    path('generate/', views.generate_recommendations_api, name='api_generate_recommendations'),
    path('weather/', weather_api.weather_api_view, name='api_weather'),
    path('weather-test/', weather_api.weather_test_view, name='api_weather_test'),
]

urlpatterns = [
    # Web interface URLs
    path('', include(web_urlpatterns)),
    
    # API URLs
    path('api/', include(api_urlpatterns)),
]
