"""
Authentication URLs for AI-Powered Personal Stylist & Wardrobe Manager
"""

from django.urls import path, include
from . import views

# Web URLs (for regular pages)
web_urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('activate/', views.EmailActivationView.as_view(), name='activate'),
]

# API URLs (for AJAX/mobile/API access)
api_urlpatterns = [
    path('register/', views.register_api, name='api_register'),
    path('login/', views.login_api, name='api_login'),
    path('logout/', views.logout_api, name='api_logout'),
]

urlpatterns = [
    # Web interface URLs
    path('', include(web_urlpatterns)),
    
    # API URLs
    path('api/', include(api_urlpatterns)),
]
