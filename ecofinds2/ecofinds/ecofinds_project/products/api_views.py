"""
API Views for EcoFinds Products
RESTful API endpoints for mobile and web applications
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q, F
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta

from .models import (
    Product, Category, Cart, CartItem, Order, 
    ChatRoom, ChatMessage, EcoChallenge, UserChallenge,
    EcoPickupZone, ProductLike
)
from .serializers import (
    ProductSerializer, CategorySerializer, CartSerializer,
    CartItemSerializer, OrderSerializer, ChatMessageSerializer,
    EcoChallengeSerializer, EcoPickupZoneSerializer
)
from accounts.models import User, EcoBadge, UserBadge
from core.ai_services import (
    image_detection_service, abuse_detection_service,
    pricing_service, sustainability_service
)
from core.translation_service import translation_service

class ProductListAPIView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating products
    """
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Product.objects.filter(status='available').select_related(
            'category', 'seller'
        ).prefetch_related('likes')
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
        
        # Category filter
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__name__icontains=category)
        
        # Condition filter
        condition = self.request.query_params.get('condition', None)
        if condition:
            queryset = queryset.filter(condition=condition)
        
        # Currency filter
        currency = self.request.query_params.get('currency', None)
        if currency:
            queryset = queryset.filter(currency=currency)
        
        # Price range filter
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Location filter
        location = self.request.query_params.get('location', None)
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        # Sort options
        sort_by = self.request.query_params.get('sort', 'created_at')
        if sort_by == 'price_low':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'popular':
            queryset = queryset.order_by('-views_count')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def perform_create(self, serializer):
        """Create a new product with AI verification"""
        product = serializer.save(seller=self.request.user)
        
        # AI Image Detection
        if product.image:
            try:
                detection_result = image_detection_service.detect_fake_image(
                    product.image.path
                )
                product.fake_detection_score = detection_result.get('confidence', 0.0)
                product.ai_verified = detection_result.get('confidence', 0.0) > 0.8
                product.manual_review_required = detection_result.get('is_fake', False)
                product.save()
            except Exception as e:
                # Log error but don't fail the creation
                pass
        
        # Calculate sustainability metrics
        if product.estimated_weight and product.category:
            try:
                sustainability_data = sustainability_service.calculate_co2_savings({
                    'category': product.category.name,
                    'weight': float(product.estimated_weight)
                })
                product.co2_saved = sustainability_data.get('co2_saved', 0.0)
                product.save()
            except Exception as e:
                pass
        
        # Award eco points to seller
        self.request.user.add_eco_points(10, "Listed a product")

class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for individual product operations
    """
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return Product.objects.select_related('category', 'seller').prefetch_related('likes')
    
    def retrieve(self, request, *args, **kwargs):
        """Increment view count when product is viewed"""
        instance = self.get_object()
        instance.increment_views()
        return super().retrieve(request, *args, **kwargs)
    
    def perform_update(self, serializer):
        """Update product with permission check"""
        product = self.get_object()
        if product.seller != self.request.user:
            return Response(
                {'error': 'You can only edit your own products'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()
    
    def perform_destroy(self, instance):
        """Delete product with permission check"""
        if instance.seller != self.request.user:
            return Response(
                {'error': 'You can only delete your own products'},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()

class CategoryListAPIView(generics.ListAPIView):
    """
    API endpoint for listing categories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_product(request, product_id):
    """
    Like or unlike a product
    """
    product = get_object_or_404(Product, id=product_id)
    like, created = ProductLike.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        product.increment_likes()
        return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)
    else:
        like.delete()
        product.likes_count = max(0, product.likes_count - 1)
        product.save()
        return Response({'status': 'unliked'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_to_cart(request, product_id):
    """
    Add product to user's cart
    """
    product = get_object_or_404(Product, id=product_id, status='available')
    
    if product.seller == request.user:
        return Response(
            {'error': 'You cannot add your own product to cart'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    serializer = CartItemSerializer(cart_item)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_cart(request):
    """
    Get user's cart
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    serializer = CartSerializer(cart)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def checkout(request):
    """
    Process checkout and create orders
    """
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()
    
    if not cart_items:
        return Response(
            {'error': 'Cart is empty'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    orders_created = []
    total_co2_saved = 0
    
    for item in cart_items:
        order = Order.objects.create(
            buyer=request.user,
            seller=item.product.seller,
            product=item.product,
            quantity=item.quantity,
            total_price=item.product.price * item.quantity
        )
        orders_created.append(order)
        
        # Mark product as sold
        item.product.status = 'sold'
        item.product.save()
        
        # Add CO2 savings
        total_co2_saved += float(item.product.co2_saved or 0)
    
    # Clear cart
    cart.items.all().delete()
    
    # Award eco points
    points_earned = len(orders_created) * 25
    request.user.add_eco_points(points_earned, "Completed purchase")
    request.user.add_co2_saved(total_co2_saved)
    
    return Response({
        'orders_created': len(orders_created),
        'total_co2_saved': total_co2_saved,
        'points_earned': points_earned
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_orders(request):
    """
    Get user's order history
    """
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_message(request, product_id):
    """
    Send a message to product seller
    """
    product = get_object_or_404(Product, id=product_id)
    
    if product.seller == request.user:
        return Response(
            {'error': 'You cannot message yourself'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get or create chat room
    chat_room, created = ChatRoom.objects.get_or_create(
        product=product,
        buyer=request.user,
        seller=product.seller
    )
    
    message_text = request.data.get('message', '')
    
    # AI Abuse Detection
    try:
        abuse_result = abuse_detection_service.detect_abuse(message_text)
        is_abusive = abuse_result.get('is_abusive', False)
        abuse_score = abuse_result.get('abuse_score', 0.0)
    except Exception:
        is_abusive = False
        abuse_score = 0.0
    
    # Create message
    message = ChatMessage.objects.create(
        room=chat_room,
        sender=request.user,
        message=message_text,
        is_abusive=is_abusive,
        abuse_score=abuse_score
    )
    
    serializer = ChatMessageSerializer(message)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_chat_messages(request, product_id):
    """
    Get chat messages for a product
    """
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user is buyer or seller
    chat_room = ChatRoom.objects.filter(
        product=product
    ).filter(
        Q(buyer=request.user) | Q(seller=request.user)
    ).first()
    
    if not chat_room:
        return Response(
            {'error': 'Chat room not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    messages = chat_room.messages.all().order_by('created_at')
    serializer = ChatMessageSerializer(messages, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_eco_challenges(request):
    """
    Get active eco challenges
    """
    challenges = EcoChallenge.objects.filter(
        is_active=True,
        end_date__gte=timezone.now()
    ).order_by('-start_date')
    
    serializer = EcoChallengeSerializer(challenges, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_pickup_zones(request):
    """
    Get available pickup zones
    """
    zones = EcoPickupZone.objects.filter(is_active=True)
    serializer = EcoPickupZoneSerializer(zones, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_stats(request):
    """
    Get user's sustainability statistics
    """
    user = request.user
    
    # Calculate stats
    total_products_sold = Product.objects.filter(seller=user, status='sold').count()
    total_products_bought = Order.objects.filter(buyer=user).count()
    total_co2_saved = float(user.co2_saved)
    
    # Get badges
    badges = UserBadge.objects.filter(user=user).select_related('badge')
    badge_data = [{
        'name': badge.badge.name,
        'description': badge.badge.description,
        'icon': badge.badge.icon,
        'earned_at': badge.earned_at
    } for badge in badges]
    
    return Response({
        'eco_points': user.eco_points,
        'eco_level': user.eco_level,
        'eco_badge': user.eco_badge,
        'co2_saved': total_co2_saved,
        'products_sold': total_products_sold,
        'products_bought': total_products_bought,
        'trust_score': user.trust_score,
        'badges': badge_data
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def translate_content(request):
    """
    Translate content to target language
    """
    content = request.data.get('content', '')
    target_language = request.data.get('target_language', 'en')
    source_language = request.data.get('source_language', 'en')
    
    if not content:
        return Response(
            {'error': 'Content is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        result = translation_service.translate_text(
            content, target_language, source_language
        )
        return Response(result)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
