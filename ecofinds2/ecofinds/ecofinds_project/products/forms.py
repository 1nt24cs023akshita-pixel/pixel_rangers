from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Category, CartItem, ChatMessage, EcoPickupZone

class ProductForm(forms.ModelForm):
    """
    Enhanced product form with AI features and smart pricing
    """
    use_smart_pricing = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'use_smart_pricing'
        }),
        help_text="Let AI suggest the best price based on market data"
    )
    
    class Meta:
        model = Product
        fields = [
            'title', 'description', 'category', 'condition', 
            'original_price', 'price', 'currency', 'image', 'video', 
            'estimated_weight', 'location'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product title',
                'maxlength': '200'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your product in detail...',
                'maxlength': '1000'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'id': 'category_select'
            }),
            'condition': forms.Select(attrs={
                'class': 'form-select'
            }),
            'original_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01',
                'id': 'original_price'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01',
                'id': 'price_input'
            }),
            'currency': forms.Select(attrs={
                'class': 'form-select',
                'id': 'currency_select'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'product_image'
            }),
            'video': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'video/*',
                'id': 'product_video'
            }),
            'estimated_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.0',
                'step': '0.1',
                'min': '0.1',
                'id': 'weight_input'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, State (optional)'
            }),
        }
        help_texts = {
            'original_price': 'Original retail price (helps calculate CO2 savings)',
            'estimated_weight': 'Weight in kg (helps calculate environmental impact)',
            'video': 'Optional video showing the product (increases trust)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add dynamic help text for categories
        if 'category' in self.fields:
            self.fields['category'].help_text = "Select the most appropriate category for accurate pricing and CO2 calculations"

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise ValidationError("Price must be greater than $0.00")
        return price

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and len(title.strip()) < 3:
            raise ValidationError("Title must be at least 3 characters long")
        return title.strip()

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and hasattr(image, 'size'):
            # Check file size (max 10MB)
            if image.size > 10 * 1024 * 1024:
                raise ValidationError("Image file too large. Maximum size is 10MB.")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if image.content_type not in allowed_types:
                raise ValidationError("Invalid image format. Please upload JPEG, PNG, GIF, or WebP.")
        
        return image

    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video and hasattr(video, 'size'):
            # Check file size (max 50MB)
            if video.size > 50 * 1024 * 1024:
                raise ValidationError("Video file too large. Maximum size is 50MB.")
            
            # Check file type
            allowed_types = ['video/mp4', 'video/avi', 'video/mov', 'video/webm']
            if video.content_type not in allowed_types:
                raise ValidationError("Invalid video format. Please upload MP4, AVI, MOV, or WebM.")
        
        return video

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        video = cleaned_data.get('video')
        original_price = cleaned_data.get('original_price')
        price = cleaned_data.get('price')
        use_smart_pricing = cleaned_data.get('use_smart_pricing')
        
        # Collect validation errors for both media types
        errors = []
        
        # Validate that both media types are provided (check if they are actual uploaded files)
        # Default values are strings, uploaded files have attributes like 'size'
        if not image or not hasattr(image, 'size'):
            errors.append("Product image is required. Please upload an image of your product.")
        
        if not video or not hasattr(video, 'size'):
            errors.append("Product video is required. Please upload a video of your product.")
        
        # If there are validation errors, raise them all at once
        if errors:
            raise ValidationError(errors)
        
        # If using smart pricing and original price is provided, calculate suggested price
        if use_smart_pricing and original_price:
            try:
                # Simple smart pricing calculation
                # In production, this would use the AI pricing service
                category = cleaned_data.get('category')
                condition = cleaned_data.get('condition', 'good')
                
                if category:
                    # Get depreciation rate from category
                    depreciation = getattr(category, 'depreciation_rate', 0.2)
                    
                    # Condition factors
                    condition_factors = {
                        'excellent': 1.0,
                        'good': 0.8,
                        'fair': 0.6,
                        'poor': 0.4,
                    }
                    
                    condition_factor = condition_factors.get(condition, 0.8)
                    suggested_price = float(original_price) * (1 - depreciation) * condition_factor
                    cleaned_data['price'] = max(suggested_price, 0.01)
                
            except Exception as e:
                # If smart pricing fails, keep the original price
                pass
        
        return cleaned_data

class ProductSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search products...',
            'id': 'search-input'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    condition = forms.ChoiceField(
        choices=[('', 'All Conditions')] + Product.CONDITION_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price',
            'step': '0.01',
            'min': '0'
        })
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price',
            'step': '0.01',
            'min': '0'
        })
    )
    currency = forms.ChoiceField(
        choices=[('', 'All Currencies')] + Product.CURRENCY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'currency_filter'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')
        
        if min_price and max_price and min_price > max_price:
            raise ValidationError("Minimum price cannot be greater than maximum price")
        
        return cleaned_data

class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10'
            })
        }

class ChatMessageForm(forms.ModelForm):
    """
    Form for chat messages with abuse detection
    """
    class Meta:
        model = ChatMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Type your message...',
                'maxlength': '500'
            })
        }

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if message and len(message.strip()) < 1:
            raise ValidationError("Message cannot be empty")
        return message.strip()

class UserProfileForm(forms.ModelForm):
    """
    Enhanced user profile form with sustainability features
    """
    class Meta:
        from accounts.models import User
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'bio', 'avatar', 'phone_number', 'location', 
            'language', 'notifications_enabled'
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '50'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '30'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '30'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'maxlength': '500',
                'placeholder': 'Tell us about your sustainability journey...'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '15',
                'placeholder': '+1 (555) 123-4567'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '100',
                'placeholder': 'City, State, Country'
            }),
            'language': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notifications_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        help_texts = {
            'bio': 'Share your sustainability story to inspire others',
            'avatar': 'Upload a profile picture to build trust',
            'language': 'Choose your preferred language for the interface'
        }

class EcoChallengeForm(forms.Form):
    """
    Form for creating eco challenges
    """
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Challenge name'
        })
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Describe the challenge...'
        })
    )
    target_co2 = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01'
        })
    )
    reward_points = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '100'
        })
    )

class PickupZoneForm(forms.ModelForm):
    """
    Form for creating eco pickup zones
    """
    class Meta:
        model = EcoPickupZone
        fields = ['name', 'address', 'latitude', 'longitude', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Zone name (e.g., "Downtown Coffee Shop")'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Full address'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'placeholder': '0.000000'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'placeholder': '0.000000'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional details about this pickup zone'
            })
        }
