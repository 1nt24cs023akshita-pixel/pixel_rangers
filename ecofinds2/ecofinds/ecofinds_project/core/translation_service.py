"""
Translation Service for EcoFinds
Handles multi-language support using various translation APIs
"""

import requests
import json
from django.conf import settings
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class TranslationService:
    """
    Service for translating content to multiple languages
    """
    
    def __init__(self):
        # API endpoints for different translation services
        self.google_translate_api = "https://translation.googleapis.com/language/translate/v2"
        self.microsoft_translate_api = "https://api.cognitive.microsofttranslator.com/translate"
        self.deepl_api = "https://api-free.deepl.com/v2/translate"
        
        # Supported languages
        self.supported_languages = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'bn': 'Bengali',
            'ta': 'Tamil',
            'te': 'Telugu',
            'ml': 'Malayalam',
            'kn': 'Kannada',
            'gu': 'Gujarati',
            'mr': 'Marathi',
            'pa': 'Punjabi'
        }
    
    def translate_text(self, text: str, target_language: str, source_language: str = 'en') -> Dict:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code (default: 'en')
            
        Returns:
            Dict with translation results
        """
        try:
            # For production, integrate with real translation APIs
            # This is a mock implementation
            
            if target_language == source_language:
                return {
                    'translated_text': text,
                    'confidence': 1.0,
                    'source_language': source_language,
                    'target_language': target_language
                }
            
            # Mock translations for demonstration
            mock_translations = {
                'es': f"[ES] {text}",
                'fr': f"[FR] {text}",
                'de': f"[DE] {text}",
                'hi': f"[HI] {text}",
                'zh': f"[ZH] {text}",
                'ar': f"[AR] {text}"
            }
            
            translated_text = mock_translations.get(target_language, f"[{target_language.upper()}] {text}")
            
            return {
                'translated_text': translated_text,
                'confidence': 0.95,
                'source_language': source_language,
                'target_language': target_language
            }
            
        except Exception as e:
            logger.error(f"Error in translation: {str(e)}")
            return {
                'translated_text': text,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def translate_product(self, product_data: Dict, target_language: str) -> Dict:
        """
        Translate product information
        
        Args:
            product_data: Dict containing product information
            target_language: Target language code
            
        Returns:
            Dict with translated product data
        """
        try:
            translated_data = product_data.copy()
            
            # Translate title and description
            if 'title' in product_data:
                title_result = self.translate_text(product_data['title'], target_language)
                translated_data['title'] = title_result['translated_text']
            
            if 'description' in product_data:
                desc_result = self.translate_text(product_data['description'], target_language)
                translated_data['description'] = desc_result['translated_text']
            
            return translated_data
            
        except Exception as e:
            logger.error(f"Error in product translation: {str(e)}")
            return product_data
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get list of supported languages
        
        Returns:
            Dict mapping language codes to language names
        """
        return self.supported_languages
    
    def detect_language(self, text: str) -> Dict:
        """
        Detect the language of given text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with language detection results
        """
        try:
            # Mock language detection - replace with actual API
            mock_response = {
                'language': 'en',
                'confidence': 0.95,
                'alternatives': [
                    {'language': 'es', 'confidence': 0.03},
                    {'language': 'fr', 'confidence': 0.02}
                ]
            }
            
            return mock_response
            
        except Exception as e:
            logger.error(f"Error in language detection: {str(e)}")
            return {
                'language': 'en',
                'confidence': 0.0,
                'error': str(e)
            }

class LocalizationService:
    """
    Service for handling localization (currency, date formats, etc.)
    """
    
    def __init__(self):
        self.currency_rates = {
            'USD': 1.0,
            'EUR': 0.85,
            'GBP': 0.73,
            'INR': 83.0,
            'JPY': 150.0,
            'CAD': 1.35,
            'AUD': 1.50
        }
    
    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> float:
        """
        Convert currency amount
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Converted amount
        """
        try:
            if from_currency == to_currency:
                return amount
            
            from_rate = self.currency_rates.get(from_currency, 1.0)
            to_rate = self.currency_rates.get(to_currency, 1.0)
            
            # Convert to USD first, then to target currency
            usd_amount = amount / from_rate
            converted_amount = usd_amount * to_rate
            
            return round(converted_amount, 2)
            
        except Exception as e:
            logger.error(f"Error in currency conversion: {str(e)}")
            return amount
    
    def format_price(self, amount: float, currency: str, locale: str = 'en_US') -> str:
        """
        Format price according to locale
        
        Args:
            amount: Price amount
            currency: Currency code
            locale: Locale code
            
        Returns:
            Formatted price string
        """
        try:
            currency_symbols = {
                'USD': '$',
                'EUR': '€',
                'GBP': '£',
                'INR': '₹',
                'JPY': '¥',
                'CAD': 'C$',
                'AUD': 'A$'
            }
            
            symbol = currency_symbols.get(currency, currency)
            
            if locale.startswith('en_IN'):
                # Indian number format
                return f"{symbol}{amount:,.2f}"
            elif locale.startswith('en_US'):
                # US number format
                return f"{symbol}{amount:,.2f}"
            else:
                # Default format
                return f"{symbol}{amount:.2f}"
                
        except Exception as e:
            logger.error(f"Error in price formatting: {str(e)}")
            return f"{amount:.2f}"

# Global service instances
translation_service = TranslationService()
localization_service = LocalizationService()

