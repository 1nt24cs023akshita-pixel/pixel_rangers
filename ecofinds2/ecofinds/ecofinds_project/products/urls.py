from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Product browsing
    path('', views.product_list, name='product_list'),
    path('product/<uuid:pk>/', views.product_detail, name='product_detail'),
    
    # Product management
    path('create/', views.create_product, name='create_product'),
    path('edit/<uuid:pk>/', views.edit_product, name='edit_product'),
    path('delete/<uuid:pk>/', views.delete_product, name='delete_product'),
    path('my-listings/', views.my_listings, name='my_listings'),
    
    # Cart functionality
    path('add-to-cart/<uuid:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('update-cart-item/<int:pk>/', views.update_cart_item, name='update_cart_item'),
    path('remove-from-cart/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    
    # Orders
    path('orders/', views.orders, name='orders'),
]
