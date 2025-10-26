"""
URL configuration for AI-Powered Personal Stylist & Wardrobe Manager
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from apps.recommendations.weather_api import weather_api_view

# Dashboard view with dynamic data
def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    from django.shortcuts import render
    from apps.wardrobe.models import ClothingItem
    from apps.recommendations.models import OutfitSuggestion
    
    # Get dynamic counts
    total_items = ClothingItem.active_objects.for_user(request.user).count()
    favorite_items = ClothingItem.active_objects.for_user(request.user).filter(is_favorite=True).count()
    outfits_created = OutfitSuggestion.objects.filter(user=request.user, is_active=True).count()
    
    # Get recent activity (last 5 items)
    recent_items = ClothingItem.active_objects.for_user(request.user).order_by('-created_at')[:5]
    
    context = {
        'total_items': total_items,
        'favorite_items': favorite_items,
        'outfits_created': outfits_created,
        'recent_items': recent_items,
    }
    
    return render(request, 'dashboard.html', context)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('', include('apps.authentication.urls')),
    path('auth/', include('apps.authentication.urls')),
    
    # Main dashboard
    path('dashboard/', dashboard_view, name='dashboard'),
    
    # App URLs
    path('wardrobe/', include('apps.wardrobe.urls')),
    path('style-me/', include('apps.recommendations.urls')),
    path('', include('apps.common.urls')),
    
    # Root-level API endpoints
    path('api/weather/', weather_api_view, name='api_weather'),
    # path('api/', include('apps.api.urls')),  # For REST API endpoints
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
