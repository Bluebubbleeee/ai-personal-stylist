"""
OpenAI Vision API Integration for Computer Vision Analysis
Handles image analysis using OpenAI's GPT-4 Vision model
"""

import base64
import json
import logging
from openai import OpenAI
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

def encode_image_to_base64(image_file):
    """
    Encode image file to base64 string
    """
    try:
        # Read the file content
        image_content = image_file.read()
        # Encode to base64
        base64_string = base64.b64encode(image_content).decode('utf-8')
        return base64_string
    except Exception as e:
        logger.error(f"Error encoding image to base64: {str(e)}")
        raise

@csrf_exempt
@require_http_methods(["GET"])
def test_openai_api(request):
    """Test endpoint to debug OpenAI API"""
    try:
        client = OpenAI(api_key="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")
        
        # Simple test without image
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": "Hello, respond with just 'OpenAI API is working'"
                }
            ],
            max_tokens=50
        )
        
        return JsonResponse({
            'success': True,
            'message': 'OpenAI API test successful',
            'response': response.choices[0].message.content
        })
        
    except Exception as e:
        logger.error(f"OpenAI test error: {str(e)}")
        return JsonResponse({
            'error': f'OpenAI test failed: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def analyze_image_openai_api(request):
    """
    OpenAI Vision API endpoint for image analysis
    Expects image file in request.FILES['image']
    Returns JSON with analyzed clothing data
    """
    try:
        # Get the image file from request
        image_file = request.FILES.get('image')
        if not image_file:
            return JsonResponse({
                'error': 'No image file provided'
            }, status=400)
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/webp']
        if image_file.content_type not in allowed_types:
            return JsonResponse({
                'error': 'Invalid file type. Please upload JPEG, PNG, or WebP image.'
            }, status=400)
        
        # Validate file size (10MB max)
        if image_file.size > 10 * 1024 * 1024:
            return JsonResponse({
                'error': 'File size too large. Maximum 10MB allowed.'
            }, status=400)
        
        # Encode image to base64
        try:
            base64_image = encode_image_to_base64(image_file)
        except Exception as e:
            logger.error(f"Image encoding error: {str(e)}")
            return JsonResponse({
                'error': 'Failed to process image'
            }, status=500)
        
        # Initialize OpenAI client (automatically picks up OPENAI_API_KEY from environment)
        try:
            openai_api_key = "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"
            client = OpenAI(api_key= openai_api_key)
        except Exception as e:
            logger.error(f"OpenAI client initialization error: {str(e)}")
            return JsonResponse({
                'error': 'OpenAI API not configured properly'
            }, status=500)
        
        # Enhanced prompt for clothing classification with dress check and description
        prompt = """You are an expert fashion classifier.
Analyze this clothing item image and provide a detailed analysis in the following JSON format:
{
  "name": "descriptive name of the item",
  "category": "main category (tops, bottoms, dresses, outerwear, shoes, accessories, underwear, activewear, formal, sleepwear, other)",
  "subcategory": "specific subcategory (e.g., t-shirt, polo, jeans, sneakers, blazer, etc.)",
  "color": "primary color",
  "secondary_color": "secondary color if applicable",
  "brand": "brand name if visible",
  "season": "appropriate season (spring, summer, fall, winter, all_season)",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10"],
  "style": "style description",
  "occasion": "suitable occasions",
  "materials": "fabric/material information",
  "fit": "fit description (loose, fitted, tight, etc.)",
  "pattern": "pattern description if any",
  "description": "concise but detailed summary of the item (2-4 sentences)"
}

Respond ONLY with valid JSON. Do not include any other text or formatting.
"""
        
        logger.info("Sending request to OpenAI Vision API for image analysis")
        
        # Make API request to OpenAI
        try:
            response = client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4o for vision capabilities
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )
        except Exception as e:
            logger.error(f"OpenAI API request error: {str(e)}")
            return JsonResponse({
                'error': f'OpenAI API error: {str(e)}'
            }, status=500)
        
        # Extract content from response
        if not response.choices or not response.choices[0].message.content:
            return JsonResponse({
                'error': 'No analysis results from OpenAI API'
            }, status=500)
        
        content = response.choices[0].message.content
        if content.startswith("I'm sorry,"):
            content = "{\"is_dress\": false}"
        
        # Parse the JSON response from OpenAI
        try:
            # Clean the response content (remove any markdown formatting)
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # Parse JSON using json.loads() as specified
            analyzed_data = json.loads(content)
            if len(analyzed_data.keys()) > 2:
                analyzed_data["is_dress"] = True
            else:
                analyzed_data = {"is_dress": False}


            logger.info("Successfully analyzed image with Computer Vision AI")
            
            # Return the parsed JSON data (frontend will decide whether to populate based on is_dress)
            return JsonResponse({
                'success': True,
                'data': analyzed_data
            })
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from OpenAI response: {str(e)}")
            logger.error(f"Raw response content: {content}")
            return JsonResponse({
                'error': 'Failed to parse analysis results. Please try again.'
            }, status=500)
        
    except Exception as e:
        logger.error(f"Unexpected error in OpenAI Vision API: {str(e)}")
        return JsonResponse({
            'error': 'Internal server error during analysis'
        }, status=500)
