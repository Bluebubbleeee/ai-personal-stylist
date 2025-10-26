"""
Weather Service for AI-Powered Personal Stylist & Wardrobe Manager
Handles weather data retrieval for outfit recommendations
"""

import requests
import logging
from django.conf import settings
from django.core.cache import cache
from typing import Dict, Optional
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from .models import WeatherCache

logger = logging.getLogger(__name__)

load_dotenv(override=True)

class WeatherService:
    """Service for weather API integration"""
    
    def __init__(self):
        self.api_endpoint = getattr(settings, 'WEATHER_API_ENDPOINT', 'http://api.weatherapi.com/v1/current.json')
        self.api_key = getattr(settings, 'WEATHER_API_KEY', '')
        self.timeout = 10  # seconds
        self.cache_duration = 3600  # 1 hour in seconds
    
    def get_weather_data(self, location: str) -> Optional[Dict]:
        """
        Get weather data for a location
        
        Args:
            location: Location string (city, coordinates, etc.)
            
        Returns:
            Dict containing weather data or None if failed
        """
        try:
            # Check cache first
            cached_data = self._get_cached_weather(location)
            if cached_data:
                return cached_data
            
            # Check if we have actual API credentials
            if not self.api_key or self.api_key == 'xxxxxx' or self.api_endpoint == 'xxxxxx':
                logger.info("Using mock weather service - replace with real API credentials")
                return self._get_mock_weather(location)
            
            # Call actual weather API
            weather_data = self._call_weather_api(location)
            
            if weather_data:
                # Cache the result
                self._cache_weather_data(location, weather_data)
                return weather_data
            
            # Fallback to mock data
            return self._get_mock_weather(location)
            
        except Exception as e:
            logger.error(f"Error fetching weather data for {location}: {str(e)}")
            return self._get_mock_weather(location)
    
    def _get_cached_weather(self, location: str) -> Optional[Dict]:
        """Check for cached weather data"""
        cache_key = f"weather_{location.lower().replace(' ', '_')}"
        
        # Check Django cache first
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # Check database cache
        try:
            weather_cache = WeatherCache.objects.filter(
                location=location,
                expires_at__gt=datetime.now()
            ).first()
            
            if weather_cache:
                data = weather_cache.weather_data
                # Store in Django cache for faster access
                cache.set(cache_key, data, self.cache_duration)
                return data
                
        except Exception as e:
            logger.error(f"Error checking weather cache: {str(e)}")
        
        return None
    
    def _call_weather_api(self, location: str) -> Optional[Dict]:
        """Make actual API call to weather service"""
        try:
            # Example for OpenWeatherMap API
            url = f"{self.api_endpoint}?key={self.api_key}&q={location}&aqi=yes&units=metric"
            
            print(url)
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            print(data)
            
            # Normalize the response to our format
            normalized_data = self._normalize_weather_data(data)
            return normalized_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API request failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error processing weather API response: {str(e)}")
            return None
    
    def _normalize_weather_data(self, api_data: Dict) -> Dict:
        """Normalize weather API response to our standard format"""
        try:
            # Normalize OpenWeatherMap response
            normalized = {
                'location': api_data.get('name', 'Unknown'),
                'country': api_data.get('sys', {}).get('country', ''),
                'temperature': round(api_data.get('main', {}).get('temp', 20)),
                'feels_like': round(api_data.get('main', {}).get('feels_like', 20)),
                'humidity': api_data.get('main', {}).get('humidity', 50),
                'description': api_data.get('weather', [{}])[0].get('description', 'clear').lower(),
                'main_weather': api_data.get('weather', [{}])[0].get('main', 'Clear').lower(),
                'icon': api_data.get('weather', [{}])[0].get('icon', '01d'),
                'wind_speed': api_data.get('wind', {}).get('speed', 0),
                'visibility': api_data.get('visibility', 10000) / 1000,  # Convert to km
                'uv_index': 5,  # Would need separate UV API call
                'timestamp': datetime.now().isoformat(),
                'source': 'openweathermap'
            }
            
            # Add clothing recommendations based on weather
            normalized['clothing_suggestions'] = self._get_weather_clothing_suggestions(normalized)
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing weather data: {str(e)}")
            return self._get_mock_weather("Unknown")
    
    def _get_weather_clothing_suggestions(self, weather_data: Dict) -> Dict:
        """Get clothing suggestions based on weather conditions"""
        temp = weather_data.get('temperature', 20)
        main_weather = weather_data.get('main_weather', 'clear')
        wind_speed = weather_data.get('wind_speed', 0)
        
        suggestions = {
            'layers': 'light',
            'materials': ['cotton', 'linen'],
            'avoid': [],
            'accessories': [],
            'footwear': ['sneakers', 'casual shoes']
        }
        
        # Temperature-based suggestions
        if temp < 5:
            suggestions['layers'] = 'heavy'
            suggestions['materials'] = ['wool', 'fleece', 'down']
            suggestions['accessories'].extend(['gloves', 'scarf', 'winter hat'])
            suggestions['footwear'] = ['boots', 'warm shoes']
        elif temp < 15:
            suggestions['layers'] = 'medium'
            suggestions['materials'] = ['cotton', 'denim', 'light wool']
            suggestions['accessories'].extend(['light jacket', 'cardigan'])
            suggestions['footwear'] = ['closed shoes', 'sneakers']
        elif temp < 25:
            suggestions['layers'] = 'light'
            suggestions['materials'] = ['cotton', 'linen', 'breathable fabrics']
        else:
            suggestions['layers'] = 'minimal'
            suggestions['materials'] = ['light cotton', 'linen', 'moisture-wicking']
            suggestions['avoid'].extend(['heavy fabrics', 'dark colors'])
        
        # Weather condition adjustments
        if 'rain' in main_weather:
            suggestions['accessories'].extend(['umbrella', 'rain jacket'])
            suggestions['footwear'] = ['waterproof shoes', 'boots']
            suggestions['avoid'].extend(['suede', 'canvas'])
        
        if wind_speed > 10:  # km/h
            suggestions['avoid'].extend(['loose clothing', 'light scarves'])
            suggestions['accessories'].append('windbreaker')
        
        return suggestions
    
    def _get_mock_weather(self, location: str) -> Dict:
        """Generate mock weather data for development"""
        # Generate realistic mock data based on location
        import random
        
        # Basic mock data
        mock_temps = {
            'summer': (20, 35),
            'winter': (-5, 15),
            'spring': (10, 25),
            'fall': (5, 20)
        }
        
        # Current season approximation
        month = datetime.now().month
        if month in [12, 1, 2]:
            season = 'winter'
        elif month in [3, 4, 5]:
            season = 'spring'
        elif month in [6, 7, 8]:
            season = 'summer'
        else:
            season = 'fall'
        
        temp_range = mock_temps[season]
        temperature = random.randint(temp_range[0], temp_range[1])
        
        weather_conditions = ['clear', 'partly cloudy', 'cloudy', 'rain', 'snow']
        condition = random.choice(weather_conditions)
        
        if season == 'winter' and temperature < 0:
            condition = 'snow'
        elif season == 'summer' and temperature > 30:
            condition = 'clear'
        
        mock_data = {
            'location': location or 'Mock City',
            'country': 'XX',
            'temperature': temperature,
            'feels_like': temperature + random.randint(-3, 3),
            'humidity': random.randint(30, 80),
            'description': condition,
            'main_weather': condition.split()[0],
            'icon': '01d',
            'wind_speed': random.uniform(0, 20),
            'visibility': random.uniform(5, 15),
            'uv_index': random.randint(1, 10),
            'timestamp': datetime.now().isoformat(),
            'source': 'mock_service'
        }
        
        # Add clothing suggestions
        mock_data['clothing_suggestions'] = self._get_weather_clothing_suggestions(mock_data)
        
        logger.info(f"Generated mock weather data for {location}: {temperature}°C, {condition}")
        return mock_data
    
    def _cache_weather_data(self, location: str, weather_data: Dict):
        """Cache weather data in database and Django cache"""
        try:
            # Cache in Django cache for fast access
            cache_key = f"weather_{location.lower().replace(' ', '_')}"
            cache.set(cache_key, weather_data, self.cache_duration)
            
            # Cache in database for persistence
            WeatherCache.objects.update_or_create(
                location=location,
                defaults={
                    'weather_data': weather_data,
                    'expires_at': datetime.now() + timedelta(seconds=self.cache_duration)
                }
            )
            
        except Exception as e:
            logger.error(f"Error caching weather data: {str(e)}")


# Service instance
weather_service = WeatherService()


def get_weather_data(location: str) -> Optional[Dict]:
    """
    Convenience function to get weather data
    
    Args:
        location: Location string
        
    Returns:
        Weather data dict or None
    """
    return weather_service.get_weather_data(location)


def get_weather_recommendations(weather_data: Dict) -> Dict:
    """
    Get clothing recommendations based on weather
    
    Args:
        weather_data: Weather data dictionary
        
    Returns:
        Clothing recommendations
    """
    return weather_data.get('clothing_suggestions', {})
