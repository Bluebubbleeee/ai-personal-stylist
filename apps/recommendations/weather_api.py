"""
Weather API Integration for AI Stylist
Handles real-time weather data from WeatherAPI.com
"""

import requests
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET"])
def weather_test_view(request):
    """Simple test endpoint to verify weather API is working"""
    return JsonResponse({
        'status': 'ok',
        'message': 'Weather API endpoint is accessible',
        'settings': {
            'api_url': settings.WEATHER_API_ENDPOINT,
            'api_key_set': bool(settings.WEATHER_API_KEY and settings.WEATHER_API_KEY != 'xxxxxx')
        }
    })

@csrf_exempt
@require_http_methods(["GET"])
def weather_api_view(request):
    """
    Weather API endpoint that fetches real-time weather data
    using user's latitude and longitude coordinates
    """
    try:
        # Get coordinates from request parameters
        lat = request.GET.get('lat')
        lon = request.GET.get('lon')
        
        if not lat or not lon:
            return JsonResponse({
                'error': 'Latitude and longitude parameters are required'
            }, status=400)
        
        # Validate coordinates
        try:
            lat_float = float(lat)
            lon_float = float(lon)
            
            if not (-90 <= lat_float <= 90) or not (-180 <= lon_float <= 180):
                return JsonResponse({
                    'error': 'Invalid coordinates. Latitude must be between -90 and 90, longitude between -180 and 180'
                }, status=400)
                
        except ValueError:
            return JsonResponse({
                'error': 'Invalid coordinate format. Must be valid decimal numbers'
            }, status=400)
        
        # Prepare API request
        api_url = settings.WEATHER_API_ENDPOINT
        api_key = settings.WEATHER_API_KEY
        
        # Format coordinates as required by WeatherAPI
        query = f"{lat_float},{lon_float}"
        
        params = {
            'key': api_key,
            'q': query,
            'aqi': 'yes'  # Include air quality data
        }
        
        logger.info(f"Fetching weather data for coordinates: {query}")
        logger.info(f"API URL: {api_url}")
        logger.info(f"API Key: {api_key[:10]}...")
        
        # Make API request with timeout
        try:
            # Try with explicit headers
            headers = {
                'User-Agent': 'AI-Stylist/1.0',
                'Accept': 'application/json'
            }
            response = requests.get(
                api_url,
                params=params,
                headers=headers,
                timeout=15,
                verify=True
            )
            logger.info(f"Weather API response status: {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            return JsonResponse({
                'error': 'Unable to connect to weather service. Please check your internet connection.'
            }, status=503)
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout error: {str(e)}")
            return JsonResponse({
                'error': 'Weather service request timeout'
            }, status=504)
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            return JsonResponse({
                'error': f'Weather service error: {str(e)}'
            }, status=503)
        
        # Handle HTTP errors
        if response.status_code == 400:
            return JsonResponse({
                'error': 'Bad request - invalid coordinates or parameters'
            }, status=400)
        elif response.status_code == 401:
            return JsonResponse({
                'error': 'Unauthorized - invalid API key'
            }, status=401)
        elif response.status_code == 403:
            return JsonResponse({
                'error': 'Forbidden - API access denied'
            }, status=403)
        elif response.status_code == 404:
            return JsonResponse({
                'error': 'Location not found'
            }, status=404)
        elif response.status_code == 429:
            return JsonResponse({
                'error': 'API rate limit exceeded'
            }, status=429)
        elif response.status_code != 200:
            return JsonResponse({
                'error': f'Weather API error: HTTP {response.status_code}'
            }, status=response.status_code)
        
        # Parse response
        try:
            weather_data = response.json()
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON response from weather API'
            }, status=500)
        
        # Check for API error in response
        if 'error' in weather_data:
            return JsonResponse({
                'error': f"Weather API error: {weather_data['error'].get('message', 'Unknown error')}"
            }, status=400)
        
        # Validate required fields
        required_fields = ['location', 'current']
        for field in required_fields:
            if field not in weather_data:
                return JsonResponse({
                    'error': f'Invalid weather data: missing {field}'
                }, status=500)
        
        # Log successful request
        logger.info(f"Weather data fetched successfully for {weather_data.get('location', {}).get('name', 'Unknown location')}")
        
        # Return weather data
        return JsonResponse(weather_data)
        
    except requests.exceptions.Timeout:
        logger.error("Weather API request timeout")
        return JsonResponse({
            'error': 'Weather API request timeout'
        }, status=504)
        
    except requests.exceptions.ConnectionError:
        logger.error("Weather API connection error")
        return JsonResponse({
            'error': 'Unable to connect to weather service'
        }, status=503)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Weather API request error: {str(e)}")
        return JsonResponse({
            'error': 'Weather service unavailable'
        }, status=503)
        
    except Exception as e:
        logger.error(f"Unexpected error in weather API: {str(e)}")
        return JsonResponse({
            'error': 'Internal server error'
        }, status=500)
