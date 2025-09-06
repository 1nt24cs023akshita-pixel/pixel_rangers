"""
API URL patterns for EcoFinds
RESTful API endpoints for mobile and web applications
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

# Create router for ViewSets (if any)
router = DefaultRouter()

# API URL patterns
api_urlpatterns = [
    # Product endpoints
    path('products/', api_views.ProductListAPIView.as_view(), name='api-product-list'),
    path('products/<uuid:pk>/', api_views.ProductDetailAPIView.as_view(), name='api-product-detail'),
    path('products/<uuid:product_id>/like/', api_views.like_product, name='api-product-like'),
    path('products/<uuid:product_id>/message/', api_views.send_message, name='api-send-message'),
    path('products/<uuid:product_id>/messages/', api_views.get_chat_messages, name='api-chat-messages'),
    
    # Category endpoints
    path('categories/', api_views.CategoryListAPIView.as_view(), name='api-category-list'),
    
    # Cart endpoints
    path('cart/', api_views.get_cart, name='api-cart'),
    path('cart/add/<uuid:product_id>/', api_views.add_to_cart, name='api-add-to-cart'),
    path('checkout/', api_views.checkout, name='api-checkout'),
    
    # Order endpoints
    path('orders/', api_views.get_orders, name='api-orders'),
    
    # Eco features endpoints
    path('challenges/', api_views.get_eco_challenges, name='api-eco-challenges'),
    path('pickup-zones/', api_views.get_pickup_zones, name='api-pickup-zones'),
    
    # User endpoints
    path('user/stats/', api_views.get_user_stats, name='api-user-stats'),
    
    # Translation endpoints
    path('translate/', api_views.translate_content, name='api-translate'),
    
    # Include router URLs
    path('', include(router.urls)),
]

