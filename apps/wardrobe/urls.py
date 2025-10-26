"""
Wardrobe URLs for AI-Powered Personal Stylist & Wardrobe Manager
"""

from django.urls import path, include
from . import views

# Web URLs (for regular pages)
web_urlpatterns = [
    path('', views.WardrobeView.as_view(), name='wardrobe'),
    path('upload/', views.UploadView.as_view(), name='wardrobe_upload'),
    path('item/<uuid:item_id>/', views.ItemDetailView.as_view(), name='item_detail'),
    path('item/<uuid:item_id>/edit/', views.EditItemView.as_view(), name='edit_item'),
    path('item/<uuid:item_id>/delete/', views.delete_item_view, name='delete_item'),
    path('item/<uuid:item_id>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
]

# API URLs (for AJAX/mobile/API access)
api_urlpatterns = [
    path('items/', views.wardrobe_api, name='api_wardrobe_list'),
    path('items/upload/', views.upload_item_api, name='api_wardrobe_upload'),
    path('items/<uuid:item_id>/', views.item_detail_api, name='api_wardrobe_detail'),
    path('stats/', views.wardrobe_stats_api, name='api_wardrobe_stats'),
    path('analyze-image-openai/', views.analyze_image_openai_api, name='api_analyze_image_openai'),
    path('test-openai/', views.test_openai_api, name='api_test_openai'),
]

urlpatterns = [
    # Web interface URLs
    path('', include(web_urlpatterns)),
    
    # API URLs
    path('api/', include(api_urlpatterns)),
]
