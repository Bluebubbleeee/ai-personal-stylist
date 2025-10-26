"""
AI Outfit Recommendation Service
Uses OpenAI API to generate intelligent outfit recommendations
"""

import json
import logging
from typing import Dict, List, Optional
from openai import OpenAI
from django.conf import settings
from apps.wardrobe.models import ClothingItem
from apps.recommendations.models import OutfitSuggestion, RecommendationSession
from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger(__name__)

class AIOutfitService:
    """Service for AI-powered outfit recommendations using OpenAI"""
    
    def __init__(self):
        # Use OpenAI API key from environment
        self.client = OpenAI()  # Automatically picks up OPENAI_API_KEY from environment
        self.model = "gpt-4o"
    
    def generate_outfit_recommendations(self, user, session: RecommendationSession, weather_data: Dict = None, occasion: str = None, custom_prompt: str = None) -> List[OutfitSuggestion]:
        """
        Generate AI-powered outfit recommendations
        
        Args:
            user: Django user object
            session: RecommendationSession object
            weather_data: Weather data dict (optional)
            
        Returns:
            List of OutfitSuggestion objects
        """
        try:
            # Get user's wardrobe items with cv_description
            wardrobe_items = ClothingItem.active_objects.for_user(user).exclude(cv_description='')
            
            if wardrobe_items.count() < 2:
                logger.warning(f"User {user.id} has insufficient wardrobe items for recommendations")
                return []
            
            # Get user's style preferences
            user_preferences = self._get_user_preferences(user)
            
            # Prepare wardrobe data for AI
            wardrobe_data = self._prepare_wardrobe_data(wardrobe_items)
            
            # Create AI prompt
            prompt = self._create_ai_prompt(session, wardrobe_data, weather_data, occasion, custom_prompt, user_preferences)
            
            # Call OpenAI API
            ai_response = self._call_openai_api(prompt)
            
            if not ai_response:
                logger.error("OpenAI API returned no response")
                return []
            
            # Parse AI response and create outfit suggestions
            recommendations = self._parse_ai_response(ai_response, user, session, wardrobe_items)
            
            logger.info(f"Generated {len(recommendations)} AI outfit recommendations for user {user.pk}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating AI outfit recommendations: {str(e)}")
            # Don't create error suggestions - just return empty list
            # This prevents failed recommendations from appearing in recent suggestions
            return []
    
    def _prepare_wardrobe_data(self, wardrobe_items) -> List[Dict]:
        """Prepare wardrobe data for AI analysis"""
        wardrobe_data = []
        
        for item in wardrobe_items:
            item_data = {
                'id': str(item.item_id),
                'name': item.name,
                'category': item.category,
                'subcategory': item.subcategory,
                'color': item.color,
                'secondary_color': item.secondary_color,
                'brand': item.brand,
                'season': item.season,
                'is_favorite': item.is_favorite,
                'wear_count': item.wear_count,
                'description': item.cv_description,  # AI-generated description
                'tags': [tag.tag for tag in item.tags.all()]
            }
            wardrobe_data.append(item_data)
        
        return wardrobe_data
    
    def _get_user_preferences(self, user) -> Dict:
        """Get user's style preferences from their profile"""
        try:
            from apps.authentication.models import UserProfile
            
            # Get or create user profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            preferences = {
                'favorite_colors': profile.style_prefs.get('favorite_colors', []),
                'favorite_styles': profile.style_prefs.get('favorite_styles', []),
                'favorite_occasions': profile.style_prefs.get('favorite_occasions', []),
                'size_preference': profile.style_prefs.get('size_preference', ''),
                'comfort_level': profile.style_prefs.get('comfort_level', ''),
                'preferred_weather_unit': profile.preferred_weather_unit,
                'location': profile.last_known_location
            }
            
            return preferences
            
        except Exception as e:
            logger.warning(f"Could not retrieve user preferences for {user.pk}: {str(e)}")
            return {
                'favorite_colors': [],
                'favorite_styles': [],
                'favorite_occasions': [],
                'size_preference': '',
                'comfort_level': '',
                'preferred_weather_unit': 'celsius',
                'location': ''
            }
    
    def _create_ai_prompt(self, session: RecommendationSession, wardrobe_data: List[Dict], weather_data: Dict = None, occasion: str = None, custom_prompt: str = None, user_preferences: Dict = None) -> str:
        """Create comprehensive AI prompt for outfit recommendations"""
        
        # Weather context
        weather_context = ""
        if weather_data:
            weather_context = f"""
Weather Context:
- Temperature: {weather_data.get('temperature', 'N/A')}°C
- Condition: {weather_data.get('condition', 'N/A')}
- Location: {session.location}
"""
        
        # User preferences context
        preferences_context = ""
        if user_preferences:
            prefs = user_preferences
            preferences_context = f"""
User Style Preferences:
- Favorite Colors: {', '.join(prefs.get('favorite_colors', [])) or 'No specific color preferences'}
- Favorite Styles: {', '.join(prefs.get('favorite_styles', [])) or 'No specific style preferences'}
- Favorite Occasions: {', '.join(prefs.get('favorite_occasions', [])) or 'No specific occasion preferences'}
- Size Preference: {prefs.get('size_preference', 'Not specified')}
- Comfort Level: {prefs.get('comfort_level', 'Not specified')}
- Preferred Weather Unit: {prefs.get('preferred_weather_unit', 'celsius')}
- Location: {prefs.get('location', 'Not specified')}
"""
        
        prompt = f"""You are an expert personal stylist and fashion consultant. Generate outfit recommendations based on the user's wardrobe and preferences. Be creative and encouraging - work with what they have and suggest additional items that would complete their look.

User Request:
- Occasion: {occasion or 'casual'}
- Custom Prompt: {custom_prompt or 'No specific preferences'}
- Location: {session.location or 'Not specified'}

{weather_context}

{preferences_context}

User's Wardrobe ({len(wardrobe_data)} items):
{json.dumps(wardrobe_data, indent=2)}

Instructions:
1. Create outfit combinations using available items from the wardrobe
2. Each outfit should be appropriate for the occasion and weather
3. PRIORITIZE the user's style preferences - if they have favorite colors, styles, or occasions, incorporate these into your recommendations
4. Consider color harmony, style coordination, and user preferences
5. If you have limited items, suggest what you can and mention what additional items would complete the outfit
6. Prioritize favorite items and consider wear frequency
7. Provide detailed rationale for each outfit choice, explaining how it aligns with their preferences
8. In your rationale, suggest additional items the user might want to consider for a complete look
9. If the user has specific style preferences (e.g., "casual", "formal"), try to match those styles
10. If the user has favorite colors, try to incorporate those colors or complementary colors

IMPORTANT: Always try to create outfit recommendations, even with minimal items. If you have limited items, suggest what you can and encourage the user to consider additional items that would complete the outfit.

Return ONLY valid JSON in this exact format:
{{
  "outfits": [
    {{
      "outfit_id": "outfit_1",
      "items": ["item_id_1", "item_id_2", "item_id_3"],
      "rationale": "Detailed explanation of why this outfit works for the occasion. Include suggestions for additional items that would complete the look.",
      "confidence": 0.85,
      "style_notes": "Additional style tips and coordination details",
      "weather_appropriateness": "How this outfit handles the weather conditions",
      "suggested_additions": ["Consider adding a statement necklace", "A belt would complete this look", "Some earrings would be perfect"]
    }}
  ]
}}

Rules:
- Use only items from the provided wardrobe
- Each outfit should have 2-5 items
- Be specific about why each combination works
- Consider the user's custom prompt and preferences
- ALWAYS incorporate user's style preferences when possible
- Respond with JSON ONLY, no additional text"""

        return prompt
    
    def _call_openai_api(self, prompt: str) -> Optional[Dict]:
        """Call OpenAI API for outfit recommendations"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert personal stylist. Analyze wardrobe items and create perfect outfit combinations. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
            # Clean response content
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            return None
    
    def _parse_ai_response(self, ai_response: Dict, user, session: RecommendationSession, wardrobe_items) -> List[OutfitSuggestion]:
        """Parse AI response and create OutfitSuggestion objects"""
        recommendations = []
        
        try:
            outfits = ai_response.get('outfits', [])
            
            if not outfits:
                logger.warning("AI response contains no outfits")
                return []
            
            for outfit_data in outfits:
                try:
                    # Validate outfit data before creating suggestion
                    if not self._validate_outfit_data(outfit_data):
                        logger.warning(f"Invalid outfit data: {outfit_data}")
                        continue
                    
                    # Create outfit suggestion
                    rationale = outfit_data.get('rationale', '')
                    suggested_additions = outfit_data.get('suggested_additions', [])
                    if suggested_additions:
                        rationale += f"\n\nSuggested additions: {', '.join(suggested_additions)}"
                    
                    suggestion = OutfitSuggestion.objects.create(
                        user=user,
                        prompt=session.original_prompt,
                        location=session.location,
                        weather=session.weather_data,
                        ai_rationale=rationale,
                        confidence_score=outfit_data.get('confidence', 0.8),
                        model_version=self.model,
                        is_active=True  # Explicitly mark as active
                    )
                    
                    # Add items to suggestion
                    item_ids = outfit_data.get('items', [])
                    valid_items = []
                    
                    for item_id in item_ids:
                        try:
                            item = wardrobe_items.get(item_id=item_id)
                            valid_items.append(item)
                        except ClothingItem.DoesNotExist:
                            logger.warning(f"Item {item_id} not found in wardrobe")
                    
                    if valid_items:
                        # Update JSON fields (no many-to-many relationship exists)
                        suggestion.items_included = [str(item.item_id) for item in valid_items]
                        suggestion.outfit_structure = {
                            'tops': [str(item.item_id) for item in valid_items if item.category == 'tops'],
                            'bottoms': [str(item.item_id) for item in valid_items if item.category == 'bottoms'],
                            'shoes': [str(item.item_id) for item in valid_items if item.category == 'shoes'],
                            'accessories': [str(item.item_id) for item in valid_items if item.category == 'accessories'],
                            'outerwear': [str(item.item_id) for item in valid_items if item.category == 'outerwear']
                        }
                        suggestion.save()
                        recommendations.append(suggestion)
                    else:
                        # If no valid items, delete the suggestion to avoid incomplete recommendations
                        suggestion.delete()
                        logger.warning("Deleted suggestion with no valid items")
                        
                except Exception as e:
                    logger.error(f"Error creating individual outfit suggestion: {str(e)}")
                    continue
                
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
        
        return recommendations
    
    def _validate_outfit_data(self, outfit_data: Dict) -> bool:
        """Validate that outfit data contains required fields"""
        required_fields = ['items', 'rationale']
        
        for field in required_fields:
            if field not in outfit_data or not outfit_data[field]:
                return False
        
        # Check that items is a list and not empty
        if not isinstance(outfit_data['items'], list) or len(outfit_data['items']) == 0:
            return False
        
        # Check that rationale is not empty
        if not outfit_data['rationale'].strip():
            return False
        
        return True
    
    def _create_error_suggestion(self, user, session, error_message):
        """Create a helpful error suggestion when AI fails"""
        try:
            from .models import OutfitSuggestion
            
            # Determine the reason for failure
            if "api" in error_message.lower() or "connection" in error_message.lower():
                reason = "Our AI service is temporarily unavailable. Please try again in a few moments."
            elif "weather" in error_message.lower():
                reason = "Weather data couldn't be processed. Try again or disable weather consideration."
            else:
                reason = "Our AI stylist encountered an issue. Please try again or contact support if the problem persists."
            
            # Create a special suggestion that explains the issue
            error_suggestion = OutfitSuggestion.objects.create(
                user=user,
                prompt=session.original_prompt,
                location=session.location,
                weather=session.weather_data,
                ai_rationale=f"AI Recommendation Error: {reason}",
                confidence_score=0.0,
                is_active=False  # Mark as inactive so it doesn't show in normal recommendations
            )
            
            return error_suggestion
            
        except Exception as e:
            logger.error(f"Error creating error suggestion: {str(e)}")
            return None
