from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from PIL import Image
import io
from .models import Product, Category
from .forms import ProductForm

User = get_user_model()

class ProductFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Electronics',
            avg_co2_per_kg=5.0,
            depreciation_rate=0.3
        )

    def create_test_image(self, filename='test_image.jpg'):
        """Create a valid test image file"""
        # Create a simple 1x1 pixel image
        image = Image.new('RGB', (1, 1), color='red')
        image_io = io.BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)
        return SimpleUploadedFile(
            filename,
            image_io.getvalue(),
            content_type='image/jpeg'
        )

    def test_form_validation_requires_both_media(self):
        """Test that form validation requires both image and video"""
        form_data = {
            'title': 'Test Product',
            'description': 'A test product description',
            'category': self.category.id,
            'condition': 'good',
            'price': 50.00,
            'currency': 'USD',
        }
        
        # Test with no media - should fail
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Product image is required', str(form.errors))
        self.assertIn('Product video is required', str(form.errors))

    def test_form_validation_with_image_only_fails(self):
        """Test that form validation fails with image only (video required)"""
        # Create a valid test image
        image = self.create_test_image()
        
        form_data = {
            'title': 'Test Product',
            'description': 'A test product description',
            'category': self.category.id,
            'condition': 'good',
            'price': 50.00,
            'currency': 'USD',
        }
        
        form = ProductForm(data=form_data, files={'image': image})
        self.assertFalse(form.is_valid())
        self.assertIn('Product video is required', str(form.errors))

    def test_form_validation_with_video_only_fails(self):
        """Test that form validation fails with video only (image required)"""
        # Create a simple test video
        video = SimpleUploadedFile(
            "test_video.mp4",
            b"fake video content",
            content_type="video/mp4"
        )
        
        form_data = {
            'title': 'Test Product',
            'description': 'A test product description',
            'category': self.category.id,
            'condition': 'good',
            'price': 50.00,
            'currency': 'USD',
        }
        
        form = ProductForm(data=form_data, files={'video': video})
        self.assertFalse(form.is_valid())
        self.assertIn('Product image is required', str(form.errors))

    def test_form_validation_with_both_media(self):
        """Test that form validation passes with both image and video"""
        # Create test files
        image = self.create_test_image()
        video = SimpleUploadedFile(
            "test_video.mp4",
            b"fake video content",
            content_type="video/mp4"
        )
        
        form_data = {
            'title': 'Test Product',
            'description': 'A test product description',
            'category': self.category.id,
            'condition': 'good',
            'price': 50.00,
            'currency': 'USD',
        }
        
        form = ProductForm(data=form_data, files={'image': image, 'video': video})
        self.assertTrue(form.is_valid())

class ProductSearchFormTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Electronics',
            avg_co2_per_kg=5.0,
            depreciation_rate=0.3
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_search_form_currency_field(self):
        """Test that currency field is present in search form"""
        from .forms import ProductSearchForm
        form = ProductSearchForm()
        self.assertIn('currency', form.fields)
        self.assertEqual(form.fields['currency'].required, False)

    def test_search_form_currency_choices(self):
        """Test that currency field has correct choices"""
        from .forms import ProductSearchForm
        form = ProductSearchForm()
        currency_choices = form.fields['currency'].choices
        self.assertIn(('', 'All Currencies'), currency_choices)
        self.assertIn(('USD', 'US Dollar ($)'), currency_choices)
        self.assertIn(('EUR', 'Euro (€)'), currency_choices)

    def test_search_form_currency_validation(self):
        """Test currency field validation"""
        from .forms import ProductSearchForm
        form_data = {
            'search': 'test',
            'currency': 'USD'
        }
        form = ProductSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['currency'], 'USD')

    def test_search_form_invalid_currency(self):
        """Test invalid currency selection"""
        from .forms import ProductSearchForm
        form_data = {
            'search': 'test',
            'currency': 'INVALID'
        }
        form = ProductSearchForm(data=form_data)
        self.assertFalse(form.is_valid())
