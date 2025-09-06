"""
Serializers for EcoFinds API
Converts model instances to JSON and vice versa
"""

from rest_framework import serializers
from .models import (
    Product, Category, Cart, CartItem, Order,
    ChatRoom, ChatMessage, EcoChallenge, UserChallenge,
    EcoPickupZone, ProductLike
)
from accounts.models import User, EcoBadge, UserBadge

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'color', 'avg_co2_per_kg', 'depreciation_rate']

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model (public information only)
    """
    eco_badge = serializers.CharField(source='get_eco_badge', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'full_name',
            'avatar', 'eco_points', 'eco_level', 'eco_badge', 'co2_saved',
            'trust_score', 'is_verified', 'created_at'
        ]

class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model
    """
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    seller = UserSerializer(read_only=True)
    formatted_price = serializers.CharField(source='get_formatted_price', read_only=True)
    is_available = serializers.BooleanField(source='get_is_available', read_only=True)
    condition_display = serializers.CharField(source='get_condition_display', read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    views_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'category', 'category_id',
            'condition', 'condition_display', 'original_price', 'price',
            'formatted_price', 'image', 'video', 'estimated_weight',
            'co2_saved', 'sustainability_score', 'seller', 'location',
            'status', 'is_available', 'ai_verified', 'fake_detection_score',
            'likes_count', 'views_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'seller', 'ai_verified', 'fake_detection_score',
            'co2_saved', 'sustainability_score', 'likes_count', 'views_count',
            'created_at', 'updated_at'
        ]

class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for CartItem model
    """
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_id', 'quantity', 'total_price', 'added_at'
        ]
        read_only_fields = ['id', 'total_price', 'added_at']

class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for Cart model
    """
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(source='get_total_items', read_only=True)
    total_price = serializers.DecimalField(source='get_total_price', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'items', 'total_items', 'total_price',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'total_items', 'total_price', 'created_at', 'updated_at']

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order model
    """
    product = ProductSerializer(read_only=True)
    buyer = UserSerializer(read_only=True)
    seller = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'product', 'buyer', 'seller', 'quantity',
            'total_price', 'status', 'status_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'buyer', 'seller', 'total_price',
            'created_at', 'updated_at'
        ]

class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for ChatMessage model
    """
    sender = UserSerializer(read_only=True)
    sender_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'sender', 'sender_id', 'message', 'is_abusive',
            'abuse_score', 'created_at'
        ]
        read_only_fields = ['id', 'is_abusive', 'abuse_score', 'created_at']

class ChatRoomSerializer(serializers.ModelSerializer):
    """
    Serializer for ChatRoom model
    """
    product = ProductSerializer(read_only=True)
    buyer = UserSerializer(read_only=True)
    seller = UserSerializer(read_only=True)
    messages = ChatMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'product', 'buyer', 'seller', 'messages',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class EcoChallengeSerializer(serializers.ModelSerializer):
    """
    Serializer for EcoChallenge model
    """
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = EcoChallenge
        fields = [
            'id', 'name', 'description', 'target_co2',
            'start_date', 'end_date', 'is_active', 'reward_points'
        ]
        read_only_fields = ['id', 'is_active']

class UserChallengeSerializer(serializers.ModelSerializer):
    """
    Serializer for UserChallenge model
    """
    challenge = EcoChallengeSerializer(read_only=True)
    challenge_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = UserChallenge
        fields = [
            'id', 'challenge', 'challenge_id', 'co2_saved',
            'is_completed', 'completed_at'
        ]
        read_only_fields = ['id', 'is_completed', 'completed_at']

class EcoPickupZoneSerializer(serializers.ModelSerializer):
    """
    Serializer for EcoPickupZone model
    """
    class Meta:
        model = EcoPickupZone
        fields = [
            'id', 'name', 'address', 'latitude', 'longitude',
            'description', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class EcoBadgeSerializer(serializers.ModelSerializer):
    """
    Serializer for EcoBadge model
    """
    class Meta:
        model = EcoBadge
        fields = [
            'id', 'name', 'description', 'icon', 'color',
            'points_required', 'co2_threshold'
        ]

class UserBadgeSerializer(serializers.ModelSerializer):
    """
    Serializer for UserBadge model
    """
    badge = EcoBadgeSerializer(read_only=True)
    
    class Meta:
        model = UserBadge
        fields = ['id', 'badge', 'earned_at']
        read_only_fields = ['id', 'earned_at']

class ProductLikeSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductLike model
    """
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = ProductLike
        fields = ['id', 'user', 'product', 'created_at']
        read_only_fields = ['id', 'created_at']

# Custom serializers for specific use cases

class ProductListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for product lists
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    formatted_price = serializers.CharField(source='get_formatted_price', read_only=True)
    condition_display = serializers.CharField(source='get_condition_display', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'formatted_price', 'image', 'category_name',
            'category_icon', 'condition_display', 'co2_saved',
            'seller_name', 'location', 'likes_count', 'views_count',
            'created_at'
        ]

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile with private information
    """
    eco_badge = serializers.CharField(source='get_eco_badge', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    badges = UserBadgeSerializer(source='earned_badges', many=True, read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'bio', 'avatar', 'phone_number', 'location', 'eco_points',
            'eco_level', 'eco_badge', 'co2_saved', 'trust_score',
            'is_verified', 'language', 'notifications_enabled',
            'badges', 'created_at', 'last_activity'
        ]
        read_only_fields = [
            'id', 'eco_points', 'eco_level', 'co2_saved', 'trust_score',
            'is_verified', 'created_at', 'last_activity'
        ]

class SustainabilityStatsSerializer(serializers.Serializer):
    """
    Serializer for sustainability statistics
    """
    total_co2_saved = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_products_sold = serializers.IntegerField()
    total_products_bought = serializers.IntegerField()
    eco_points = serializers.IntegerField()
    eco_level = serializers.CharField()
    trust_score = serializers.IntegerField()
    badges_count = serializers.IntegerField()

class TranslationRequestSerializer(serializers.Serializer):
    """
    Serializer for translation requests
    """
    content = serializers.CharField(max_length=1000)
    target_language = serializers.CharField(max_length=10)
    source_language = serializers.CharField(max_length=10, default='en')

class TranslationResponseSerializer(serializers.Serializer):
    """
    Serializer for translation responses
    """
    translated_text = serializers.CharField()
    confidence = serializers.FloatField()
    source_language = serializers.CharField()
    target_language = serializers.CharField()

