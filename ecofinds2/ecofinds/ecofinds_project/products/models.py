from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid

User = get_user_model()

class Category(models.Model):
    """
    Product categories with sustainability data
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-tag')  # FontAwesome icon class
    color = models.CharField(max_length=20, default='primary')
    
    # Sustainability data for CO2 calculations
    avg_co2_per_kg = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text="Average CO2 emissions per kg for this category"
    )
    depreciation_rate = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.20,
        help_text="Depreciation rate for smart pricing (0.0-1.0)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Product(models.Model):
    """
    Enhanced Product model with AI detection and sustainability features
    """
    CONDITION_CHOICES = [
        ('excellent', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Average'),
        ('poor', 'Poor'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('pending', 'Pending'),
        ('flagged', 'Flagged for Review'),
    ]
    
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar ($)'),
        ('EUR', 'Euro (€)'),
        ('GBP', 'British Pound (£)'),
        ('INR', 'Indian Rupee (₹)'),
        ('CAD', 'Canadian Dollar (C$)'),
        ('AUD', 'Australian Dollar (A$)'),
        ('JPY', 'Japanese Yen (¥)'),
        ('CNY', 'Chinese Yuan (¥)'),
        ('BRL', 'Brazilian Real (R$)'),
        ('MXN', 'Mexican Peso ($)'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    
    # Smart Pricing
    original_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Original retail price for CO2 calculation"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='USD',
        help_text="Currency for the price"
    )
    is_smart_priced = models.BooleanField(default=False, help_text="Price calculated using smart pricing formula")
    
    # Media (Enhanced)
    image = models.ImageField(
        upload_to='products/', 
        default='products/default_product.png',
        help_text="Product image (required)"
    )
    video = models.FileField(
        upload_to='products/videos/', 
        default='products/videos/default_video.mp4',
        help_text="Product video (required)"
    )
    
    # AI Detection & Trust
    ai_verified = models.BooleanField(default=False, help_text="AI has verified this listing")
    fake_detection_score = models.FloatField(
        default=0.0,
        help_text="AI confidence score (0=fake, 1=real)"
    )
    manual_review_required = models.BooleanField(default=False)
    
    # Sustainability Data
    estimated_weight = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Estimated weight in kg for CO2 calculation"
    )
    co2_saved = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text="CO2 saved by buying this instead of new (kg)"
    )
    sustainability_score = models.PositiveIntegerField(
        default=0,
        help_text="Sustainability score (0-100)"
    )
    
    # Seller Information
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    location = models.CharField(max_length=100, blank=True)
    
    # Status and Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When this listing expires (optional)"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['seller', 'status']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Override save to calculate sustainability metrics"""
        if not self.co2_saved and self.estimated_weight and self.category:
            # Calculate CO2 saved based on category and weight
            self.co2_saved = float(self.estimated_weight) * float(self.category.avg_co2_per_kg)
        
        # Calculate smart price if original price is provided
        if self.original_price and not self.is_smart_priced:
            self.price = self.calculate_smart_price()
            self.is_smart_priced = True
        
        super().save(*args, **kwargs)
    
    def calculate_smart_price(self):
        """
        Calculate smart price using the formula:
        Resale Price = Original Price × (1 − D) × C
        Where D = depreciation rate, C = condition factor
        """
        if not self.original_price:
            return self.price
        
        # Condition factors
        condition_factors = {
            'excellent': 1.0,
            'good': 0.8,
            'fair': 0.6,
            'poor': 0.4,
        }
        
        depreciation = self.category.depreciation_rate
        condition_factor = condition_factors.get(self.condition, 0.8)
        
        smart_price = float(self.original_price) * (1 - float(depreciation)) * condition_factor
        return max(smart_price, 0.01)  # Minimum price of $0.01
    
    @property
    def is_available(self):
        return self.status == 'available'
    
    @property
    def formatted_price(self):
        """Format price with appropriate currency symbol"""
        currency_symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'INR': '₹',
            'CAD': 'C$',
            'AUD': 'A$',
            'JPY': '¥',
            'CNY': '¥',
            'BRL': 'R$',
            'MXN': '$',
        }
        symbol = currency_symbols.get(self.currency, '$')
        return f"{symbol}{self.price:.2f}"
    
    @property
    def condition_factor(self):
        """Return the condition factor for pricing"""
        factors = {
            'excellent': 1.0,
            'good': 0.8,
            'fair': 0.6,
            'poor': 0.4,
        }
        return factors.get(self.condition, 0.8)
    
    def increment_views(self):
        """Increment view count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def increment_likes(self):
        """Increment like count"""
        self.likes_count += 1
        self.save(update_fields=['likes_count'])

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Cart"
    
    @property
    def total_items(self):
        return self.items.count()
    
    @property
    def total_price(self):
        return sum(item.product.price for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f"{self.product.title} in {self.cart.user.username}'s cart"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} - {self.product.title}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)

class ChatRoom(models.Model):
    """
    Chat room between buyer and seller
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='chat_rooms')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_chats')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_chats')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['product', 'buyer', 'seller']
    
    def __str__(self):
        return f"Chat: {self.buyer.username} & {self.seller.username} - {self.product.title}"

class ChatMessage(models.Model):
    """
    Individual chat messages with abuse detection
    """
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_abusive = models.BooleanField(default=False)
    abuse_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.username}: {self.message[:50]}..."

class EcoChallenge(models.Model):
    """
    Monthly sustainability challenges
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    target_co2 = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    reward_points = models.PositiveIntegerField(default=100)
    
    def __str__(self):
        return self.name

class UserChallenge(models.Model):
    """
    Track user participation in challenges
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='challenges')
    challenge = models.ForeignKey(EcoChallenge, on_delete=models.CASCADE)
    co2_saved = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'challenge']
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.name}"

class EcoPickupZone(models.Model):
    """
    Safe handoff points for transactions
    """
    name = models.CharField(max_length=100)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class ProductLike(models.Model):
    """
    Track product likes for engagement
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product']
    
    def __str__(self):
        return f"{self.user.username} likes {self.product.title}"
