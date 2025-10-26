"""
AI Service for AI-Powered Personal Stylist & Wardrobe Manager
Handles AI-powered outfit recommendations
"""

import requests
import logging
from django.conf import settings
from typing import Dict, List, Optional
import json
import random
from datetime import datetime

logger = logging.getLogger(__name__)


class AIRecommendationService:
    """Service for AI recommendation API integration"""
    
    def __init__(self):
        self.api_endpoint = getattr(settings, 'AI_RECOMMENDATION_API_ENDPOINT', 'xxxxxx')
        self.api_key = getattr(settings, 'AI_RECOMMENDATION_API_KEY', 'xxxxxx')
        self.timeout = 30  # seconds
        self.max_retries = 2
    
    def get_outfit_recommendations(self, recommendation_request: Dict) -> List[Dict]:
        """
        Get AI-powered outfit recommendations
        
        Args:
            recommendation_request: Dict containing user preferences, weather, wardrobe items, etc.
            
        Returns:
            List of outfit recommendations
        """
        try:
            # Check if we have actual API credentials
            if self.api_endpoint == 'xxxxxx' or self.api_key == 'xxxxxx':
                logger.info("Using mock AI service - replace with real API credentials")
                return self._generate_mock_recommendations(recommendation_request)
            
            # Call actual AI API
            ai_recommendations = self._call_ai_api(recommendation_request)
            
            if ai_recommendations:
                return self._process_ai_recommendations(ai_recommendations)
            
            # Fallback to mock recommendations
            return self._generate_mock_recommendations(recommendation_request)
            
        except Exception as e:
            logger.error(f"Error getting AI recommendations: {str(e)}")
            return self._generate_mock_recommendations(recommendation_request)
    
    def _call_ai_api(self, request_data: Dict) -> Optional[Dict]:
        """Make actual API call to AI recommendation service"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
            }
            
            payload = {
                'occasion': request_data.get('occasion', 'casual'),
                'custom_prompt': request_data.get('custom_prompt', ''),
                'weather_context': request_data.get('weather', {}),
                'user_preferences': request_data.get('user_preferences', {}),
                'available_items': request_data.get('wardrobe_items', []),
                'style_constraints': {
                    'max_items_per_outfit': 5,
                    'min_items_per_outfit': 2,
                    'prefer_favorites': True,
                    'consider_wear_frequency': True
                },
                'output_format': {
                    'include_rationale': True,
                    'include_confidence': True,
                    'max_recommendations': 5
                }
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
                    logger.warning(f"AI API attempt {attempt + 1} failed: {str(e)}")
                    if attempt == self.max_retries - 1:
                        raise
            
        except Exception as e:
            logger.error(f"AI API call failed: {str(e)}")
            return None
    
    def _process_ai_recommendations(self, ai_response: Dict) -> List[Dict]:
        """Process raw AI API response into standardized format"""
        try:
            recommendations = []
            
            for rec_data in ai_response.get('recommendations', []):
                processed_rec = {
                    'items': rec_data.get('selected_items', []),
                    'rationale': rec_data.get('explanation', 'AI-generated outfit suggestion'),
                    'confidence': rec_data.get('confidence_score', 0.8),
                    'style_score': rec_data.get('style_compatibility', 0.8),
                    'weather_appropriateness': rec_data.get('weather_score', 0.8),
                    'tags': rec_data.get('style_tags', []),
                    'color_harmony': rec_data.get('color_analysis', {}),
                    'occasion_fit': rec_data.get('occasion_score', 0.8)
                }
                recommendations.append(processed_rec)
            
            return recommendations[:5]  # Limit to 5 recommendations
            
        except Exception as e:
            logger.error(f"Error processing AI recommendations: {str(e)}")
            return []
    
    def _generate_mock_recommendations(self, request_data: Dict) -> List[Dict]:
        """Generate mock AI recommendations for development"""
        try:
            occasion = request_data.get('occasion', 'casual')
            wardrobe_items = request_data.get('wardrobe_items', [])
            weather = request_data.get('weather', {})
            custom_prompt = request_data.get('custom_prompt', '')
            
            if not wardrobe_items:
                return []
            
            # Generate 3-5 mock outfit recommendations
            recommendations = []
            
            for i in range(min(3, max(1, len(wardrobe_items) // 3))):
                # Create a realistic outfit combination
                outfit_items = self._create_mock_outfit(wardrobe_items, occasion, weather)
                
                # Generate contextual rationale
                rationale = self._generate_mock_rationale(outfit_items, occasion, weather, custom_prompt)
                
                # Calculate mock confidence based on various factors
                confidence = self._calculate_mock_confidence(outfit_items, occasion, weather)
                
                recommendation = {
                    'items': outfit_items,
                    'rationale': rationale,
                    'confidence': confidence,
                    'style_score': random.uniform(0.7, 0.95),
                    'weather_appropriateness': self._calculate_weather_score(outfit_items, weather),
                    'tags': self._generate_style_tags(outfit_items, occasion),
                    'color_harmony': self._analyze_color_harmony(outfit_items),
                    'occasion_fit': random.uniform(0.75, 0.95)
                }
                
                recommendations.append(recommendation)
            
            logger.info(f"Generated {len(recommendations)} mock AI recommendations for {occasion}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating mock recommendations: {str(e)}")
            return []
    
    def _create_mock_outfit(self, wardrobe_items: List[Dict], occasion: str, weather: Dict) -> List[Dict]:
        """Create a mock outfit combination"""
        # Group items by category
        categories = {}
        for item in wardrobe_items:
            category = item.get('category', 'other')
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        # Build outfit based on occasion and weather
        outfit = []
        
        # Core pieces (top + bottom or dress)
        if 'dresses' in categories and occasion in ['formal', 'date', 'party'] and random.random() > 0.5:
            outfit.append(random.choice(categories['dresses']))
        else:
            if 'tops' in categories:
                outfit.append(random.choice(categories['tops']))
            if 'bottoms' in categories:
                outfit.append(random.choice(categories['bottoms']))
        
        # Weather-appropriate additions
        temp = weather.get('temperature', 20)
        if temp < 15 and 'outerwear' in categories:
            outfit.append(random.choice(categories['outerwear']))
        
        # Footwear
        if 'shoes' in categories:
            shoes = categories['shoes']
            if occasion == 'formal':
                formal_shoes = [s for s in shoes if any(tag in s.get('tags', []) for tag in ['formal', 'dress', 'heels'])]
                outfit.append(random.choice(formal_shoes) if formal_shoes else random.choice(shoes))
            else:
                outfit.append(random.choice(shoes))
        
        # Accessories (occasionally)
        if 'accessories' in categories and random.random() > 0.6:
            outfit.append(random.choice(categories['accessories']))
        
        return outfit[:5]  # Max 5 items per outfit
    
    def _generate_mock_rationale(self, items: List[Dict], occasion: str, weather: Dict, custom_prompt: str) -> str:
        """Generate a mock AI rationale for outfit choice"""
        rationales = {
            'casual': [
                "This relaxed combination offers comfort and style for everyday activities.",
                "Perfect for a laid-back look that's both comfortable and put-together.",
                "A versatile ensemble that works great for casual outings.",
            ],
            'work': [
                "Professional and polished, this outfit projects confidence in the workplace.",
                "A sophisticated look that balances professionalism with personal style.",
                "Clean lines and coordinated colors create a professional appearance.",
            ],
            'formal': [
                "An elegant combination perfect for formal occasions and special events.",
                "This sophisticated ensemble ensures you'll look appropriately dressed for formal settings.",
                "Classic pieces that create a timeless, formal appearance.",
            ],
            'date': [
                "A charming and stylish look that's perfect for a romantic evening.",
                "This outfit strikes the right balance between elegant and approachable.",
                "Flattering pieces that create a memorable and attractive appearance.",
            ],
            'party': [
                "Fun and festive, this combination is perfect for social gatherings.",
                "Eye-catching pieces that help you stand out at any celebration.",
                "A lively outfit that matches the energy of party atmospheres.",
            ]
        }
        
        base_rationale = random.choice(rationales.get(occasion, rationales['casual']))
        
        # Add weather context
        temp = weather.get('temperature', 20)
        if temp < 10:
            base_rationale += " The layering keeps you warm in cold weather."
        elif temp > 25:
            base_rationale += " Light fabrics and breathable materials keep you cool."
        elif weather.get('main_weather') == 'rain':
            base_rationale += " Weather-appropriate choices for rainy conditions."
        
        # Add color harmony note
        colors = [item.get('color', 'neutral') for item in items if item.get('color')]
        if colors:
            base_rationale += f" The {' and '.join(set(colors))} color palette creates visual harmony."
        
        return base_rationale
    
    def _calculate_mock_confidence(self, items: List[Dict], occasion: str, weather: Dict) -> float:
        """Calculate mock confidence score"""
        base_confidence = 0.8
        
        # Boost for favorite items
        favorites = [item for item in items if item.get('is_favorite')]
        if favorites:
            base_confidence += 0.05 * len(favorites)
        
        # Boost for weather appropriateness
        temp = weather.get('temperature', 20)
        has_outerwear = any(item.get('category') == 'outerwear' for item in items)
        
        if temp < 15 and has_outerwear:
            base_confidence += 0.1
        elif temp > 25 and not has_outerwear:
            base_confidence += 0.05
        
        # Boost for occasion match
        formal_items = [item for item in items if 'formal' in item.get('tags', [])]
        if occasion == 'formal' and formal_items:
            base_confidence += 0.1
        
        return min(0.95, base_confidence + random.uniform(-0.1, 0.1))
    
    def _calculate_weather_score(self, items: List[Dict], weather: Dict) -> float:
        """Calculate weather appropriateness score"""
        temp = weather.get('temperature', 20)
        main_weather = weather.get('main_weather', 'clear')
        
        score = 0.8
        
        # Temperature appropriateness
        has_outerwear = any(item.get('category') == 'outerwear' for item in items)
        
        if temp < 10 and has_outerwear:
            score += 0.15
        elif temp > 25 and not has_outerwear:
            score += 0.1
        elif 10 <= temp <= 25:
            score += 0.05
        
        # Weather condition appropriateness
        if 'rain' in main_weather:
            waterproof_items = [item for item in items if any(tag in item.get('tags', []) for tag in ['waterproof', 'rain'])]
            if waterproof_items:
                score += 0.1
        
        return min(0.95, score + random.uniform(-0.05, 0.05))
    
    def _generate_style_tags(self, items: List[Dict], occasion: str) -> List[str]:
        """Generate style tags for outfit"""
        tags = set()
        
        # Add occasion
        tags.add(occasion)
        
        # Add category-based tags
        categories = [item.get('category') for item in items]
        if 'dresses' in categories:
            tags.add('feminine')
        if 'outerwear' in categories:
            tags.add('layered')
        
        # Add color-based tags
        colors = [item.get('color') for item in items if item.get('color')]
        if 'black' in colors and 'white' in colors:
            tags.add('monochrome')
        elif len(set(colors)) == 1:
            tags.add('tonal')
        
        # Add random style descriptors
        style_descriptors = ['chic', 'modern', 'classic', 'trendy', 'comfortable', 'sophisticated']
        tags.add(random.choice(style_descriptors))
        
        return list(tags)[:5]
    
    def _analyze_color_harmony(self, items: List[Dict]) -> Dict:
        """Analyze color harmony of outfit"""
        colors = [item.get('color', 'neutral') for item in items if item.get('color')]
        
        harmony_types = ['complementary', 'monochromatic', 'analogous', 'triadic', 'neutral']
        
        return {
            'primary_colors': colors[:3],
            'harmony_type': random.choice(harmony_types),
            'harmony_score': random.uniform(0.7, 0.95),
            'color_balance': random.uniform(0.75, 0.9)
        }


# Service instance
ai_service = AIRecommendationService()


def get_outfit_recommendations(recommendation_request: Dict) -> List[Dict]:
    """
    Convenience function to get AI outfit recommendations
    
    Args:
        recommendation_request: Request data
        
    Returns:
        List of outfit recommendations
    """
    return ai_service.get_outfit_recommendations(recommendation_request)
