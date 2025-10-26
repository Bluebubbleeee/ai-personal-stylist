"""
Computer Vision Service for AI-Powered Personal Stylist & Wardrobe Manager
Handles image analysis and auto-tagging of clothing items
"""

import requests
import logging
from django.conf import settings
from django.utils import timezone
from typing import Dict, List, Optional, Tuple
import json
from PIL import Image
import io
import base64
from .models import ClothingItem, Tag, CanonicalTag

logger = logging.getLogger(__name__)


class ComputerVisionService:
    """Service for computer vision API integration"""
    
    def __init__(self):
        self.api_endpoint = getattr(settings, 'CV_API_ENDPOINT', '')
        self.api_key = getattr(settings, 'CV_API_KEY', '')
        self.timeout = 30  # seconds
        self.max_retries = 3
    
    def analyze_clothing_item(self, clothing_item: ClothingItem) -> Dict:
        """
        Analyze a clothing item image using computer vision API
        
        Returns:
            Dict containing analysis results with confidence scores
        """
        try:
            # Check if we have actual API credentials
            if not self.api_key or not self.api_endpoint or self.api_endpoint == 'xxxxxx' or self.api_key == 'xxxxxx':
                logger.info("Using mock CV service - replace with real API credentials")
                return self._mock_cv_analysis(clothing_item)
            
            # Prepare image for API
            image_data = self._prepare_image(clothing_item.image)
            
            # Call actual CV API
            analysis_result = self._call_cv_api(image_data)
            
            # Process and normalize results
            processed_results = self._process_cv_results(analysis_result, clothing_item)
            
            # Apply results to clothing item
            self._apply_cv_results(clothing_item, processed_results)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Error in CV analysis for item {clothing_item.item_id}: {str(e)}")
            return self._fallback_analysis(clothing_item)
    
    def _prepare_image(self, image_field) -> str:
        """Prepare image for CV API (resize, encode, etc.)"""
        try:
            # Open image
            with Image.open(image_field) as img:
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize to optimal size for CV API (max 1024x1024)
                max_size = (1024, 1024)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Convert to base64 string
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=90)
                img_str = base64.b64encode(buffer.getvalue()).decode()
                
                return img_str
                
        except Exception as e:
            logger.error(f"Error preparing image for CV analysis: {str(e)}")
            raise
    
    def _call_cv_api(self, image_data: str) -> Dict:
        """Make actual API call to computer vision service"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        
        payload = {
            'image': image_data,
            'features': [
                'object_detection',      # Detect clothing items
                'color_analysis',        # Identify primary/secondary colors
                'text_recognition',      # OCR for brand names, labels
                'style_classification',  # Classify style/category
                'attribute_detection'    # Material, pattern, etc.
            ],
            'confidence_threshold': 0.5
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.api_endpoint,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"CV API attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
    
    def _process_cv_results(self, cv_results: Dict, item: ClothingItem) -> Dict:
        """Process raw CV API results into structured format"""
        processed = {
            'category': None,
            'colors': [],
            'tags': [],
            'attributes': {},
            'confidence': 0.0,
            'brand_detected': None,
            'material_detected': None,
        }
        
        try:
            # Process object detection results
            if 'objects' in cv_results:
                clothing_objects = [
                    obj for obj in cv_results['objects'] 
                    if obj.get('category', '').lower() in ['clothing', 'apparel', 'fashion']
                ]
                
                if clothing_objects:
                    best_detection = max(clothing_objects, key=lambda x: x.get('confidence', 0))
                    processed['category'] = self._map_cv_category(best_detection.get('name', ''))
                    processed['confidence'] = best_detection.get('confidence', 0.5)
            
            # Process color analysis
            if 'colors' in cv_results:
                colors = cv_results['colors']
                if colors:
                    # Get primary and secondary colors
                    sorted_colors = sorted(colors, key=lambda x: x.get('percentage', 0), reverse=True)
                    processed['colors'] = [self._map_cv_color(c['name']) for c in sorted_colors[:2]]
            
            # Process style classification
            if 'style_class' in cv_results:
                style_info = cv_results['style_class']
                processed['tags'].extend([
                    tag for tag in style_info.get('tags', [])
                    if isinstance(tag, str) and len(tag) > 2
                ])
            
            # Process text recognition (for brands)
            if 'text' in cv_results:
                text_results = cv_results['text']
                brand_candidates = [
                    text['content'] for text in text_results
                    if text.get('confidence', 0) > 0.8 and 2 < len(text.get('content', '')) < 20
                ]
                if brand_candidates:
                    processed['brand_detected'] = brand_candidates[0]
            
            # Process attributes (material, pattern, etc.)
            if 'attributes' in cv_results:
                attrs = cv_results['attributes']
                processed['attributes'] = {
                    'material': attrs.get('material', ''),
                    'pattern': attrs.get('pattern', ''),
                    'fit': attrs.get('fit', ''),
                    'style': attrs.get('style', ''),
                }
                
                # Add attributes as tags
                for attr_type, attr_value in processed['attributes'].items():
                    if attr_value and isinstance(attr_value, str):
                        processed['tags'].append(f"{attr_type}_{attr_value.lower()}")
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing CV results: {str(e)}")
            return processed
    
    def _apply_cv_results(self, item: ClothingItem, results: Dict):
        """Apply CV analysis results to clothing item"""
        try:
            # Update category if detected with high confidence
            if results.get('category') and results.get('confidence', 0) > 0.7:
                if not item.category or item.category == 'other':
                    item.category = results['category']
            
            # Update colors if detected
            colors = results.get('colors', [])
            if colors:
                if not item.color or item.color == 'other':
                    item.color = colors[0]
                if len(colors) > 1 and not item.secondary_color:
                    item.secondary_color = colors[1]
            
            # Update brand if detected
            if results.get('brand_detected') and not item.brand:
                item.brand = results['brand_detected']
            
            # Store CV metadata
            item.cv_confidence = results.get('confidence', 0.0)
            item.cv_metadata = {
                'analysis_timestamp': str(timezone.now()),
                'detected_category': results.get('category'),
                'detected_colors': results.get('colors', []),
                'detected_brand': results.get('brand_detected'),
                'attributes': results.get('attributes', {}),
                'api_version': 'v1.0'
            }
            
            item.save()
            
            # Create CV tags
            cv_tags = results.get('tags', [])
            if cv_tags:
                for tag_name in cv_tags[:10]:  # Limit to 10 tags
                    if isinstance(tag_name, str) and len(tag_name.strip()) > 1:
                        normalized_tag = CanonicalTag.normalize_tag(tag_name.strip())
                        Tag.objects.get_or_create(
                            item=item,
                            tag=normalized_tag,
                            defaults={
                                'source': 'cv',
                                'confidence': results.get('confidence', 0.5)
                            }
                        )
            
            logger.info(f"Applied CV results to item {item.item_id}: "
                       f"category={results.get('category')}, "
                       f"tags={len(cv_tags)}, "
                       f"confidence={results.get('confidence', 0):.2f}")
            
        except Exception as e:
            logger.error(f"Error applying CV results to item {item.item_id}: {str(e)}")
    
    def _mock_cv_analysis(self, item: ClothingItem) -> Dict:
        """Mock CV analysis for development/testing"""
        # Generate mock results based on existing item data
        mock_tags = []
        mock_confidence = 0.85
        
        # Category-based mock tags
        category_tags = {
            'tops': ['shirt', 'casual', 'cotton', 'comfortable'],
            'bottoms': ['pants', 'denim', 'casual', 'everyday'],
            'shoes': ['sneakers', 'comfortable', 'athletic', 'walking'],
            'dresses': ['dress', 'elegant', 'formal', 'occasion'],
            'outerwear': ['jacket', 'warm', 'outer', 'layer'],
            'accessories': ['accessory', 'fashion', 'style'],
            'activewear': ['sport', 'athletic', 'active', 'fitness'],
            'intimates': ['intimate', 'comfortable', 'basic'],
            'sleepwear': ['sleep', 'comfortable', 'soft', 'casual'],
        }
        
        mock_tags = category_tags.get(item.category, ['clothing', 'fashion'])
        
        # Color-based tags
        if item.color and item.color != 'other':
            mock_tags.append(item.color)
        
        # Season-based tags
        if item.season and item.season != 'all_season':
            mock_tags.append(item.season)
        
        mock_results = {
            'category': item.category,
            'colors': [item.color] if item.color else ['other'],
            'tags': mock_tags[:6],  # Limit to 6 tags
            'confidence': mock_confidence,
            'brand_detected': item.brand if item.brand else None,
            'attributes': {
                'detected_via': 'mock_service',
                'style': 'casual',
                'fit': 'regular'
            }
        }
        
        logger.info(f"Generated mock CV analysis for item {item.item_id}")
        return mock_results
    
    def _fallback_analysis(self, item: ClothingItem) -> Dict:
        """Fallback analysis when CV API fails"""
        return {
            'category': item.category,
            'colors': [item.color] if item.color else [],
            'tags': ['unanalyzed'],
            'confidence': 0.3,
            'error': 'CV analysis failed, using fallback'
        }
    
    def _map_cv_category(self, cv_category: str) -> str:
        """Map CV API category to our category choices"""
        category_mapping = {
            'shirt': 'tops',
            'blouse': 'tops',
            't-shirt': 'tops',
            'sweater': 'tops',
            'hoodie': 'tops',
            'pants': 'bottoms',
            'jeans': 'bottoms',
            'shorts': 'bottoms',
            'skirt': 'bottoms',
            'dress': 'dresses',
            'gown': 'dresses',
            'shoes': 'shoes',
            'sneakers': 'shoes',
            'boots': 'shoes',
            'sandals': 'shoes',
            'jacket': 'outerwear',
            'coat': 'outerwear',
            'blazer': 'outerwear',
            'hat': 'accessories',
            'bag': 'accessories',
            'scarf': 'accessories',
            'belt': 'accessories',
        }
        
        cv_category_lower = cv_category.lower() if cv_category else ''
        return category_mapping.get(cv_category_lower, 'other')
    
    def _map_cv_color(self, cv_color: str) -> str:
        """Map CV API color to our color choices"""
        color_mapping = {
            'red': 'red',
            'blue': 'blue',
            'green': 'green',
            'yellow': 'yellow',
            'orange': 'orange',
            'purple': 'purple',
            'pink': 'pink',
            'brown': 'brown',
            'black': 'black',
            'white': 'white',
            'gray': 'gray',
            'grey': 'gray',
            'beige': 'beige',
            'navy': 'navy',
            'teal': 'teal',
            'maroon': 'maroon',
            'olive': 'olive',
            'gold': 'gold',
            'silver': 'silver',
        }
        
        cv_color_lower = cv_color.lower() if cv_color else ''
        return color_mapping.get(cv_color_lower, 'other')


# Service instance
cv_service = ComputerVisionService()


def analyze_clothing_item(item: ClothingItem) -> Dict:
    """
    Convenience function to analyze a clothing item
    
    Args:
        item: ClothingItem instance to analyze
        
    Returns:
        Dict containing analysis results
    """
    return cv_service.analyze_clothing_item(item)
