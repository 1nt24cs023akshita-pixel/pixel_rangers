from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Enhanced User model with sustainability features and gamification
    """
    # Basic authentication fields
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    
    # Profile information
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    bio = models.TextField(max_length=500, blank=True, help_text="Tell us about your sustainability journey")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    # Sustainability & Gamification
    eco_points = models.PositiveIntegerField(default=0, help_text="Points earned through sustainable actions")
    eco_level = models.CharField(
        max_length=20,
        choices=[
            ('apprentice', 'Eco Apprentice'),
            ('ninja', 'Eco Ninja'),
            ('legend', 'Eco Legend'),
        ],
        default='apprentice'
    )
    co2_saved = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text="Total CO2 saved in kg"
    )
    
    # Trust & Verification
    is_verified = models.BooleanField(default=False)
    trust_score = models.PositiveIntegerField(
        default=50,
        help_text="Trust score based on user behavior (0-100)"
    )
    
    # Preferences
    language = models.CharField(max_length=10, default='en', help_text="Preferred language code")
    notifications_enabled = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'  # Email will be used to log in
    REQUIRED_FIELDS = ['username']  # Username is still required

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username

    @property
    def eco_badge(self):
        """Return the user's current eco badge"""
        return dict(self._meta.get_field('eco_level').choices)[self.eco_level]

    def add_eco_points(self, points, reason=""):
        """Add eco points and check for level up"""
        self.eco_points += points
        
        # Check for level up
        if self.eco_points >= 1000 and self.eco_level == 'apprentice':
            self.eco_level = 'ninja'
        elif self.eco_points >= 5000 and self.eco_level == 'ninja':
            self.eco_level = 'legend'
        
        self.save(update_fields=['eco_points', 'eco_level'])
        return self.eco_level

    def add_co2_saved(self, co2_amount):
        """Add CO2 saved amount"""
        self.co2_saved += float(co2_amount)
        self.save(update_fields=['co2_saved'])

    def update_trust_score(self, change):
        """Update trust score with bounds checking"""
        self.trust_score = max(0, min(100, self.trust_score + change))
        self.save(update_fields=['trust_score'])
