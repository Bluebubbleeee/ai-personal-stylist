"""
JWT Authentication backend for AI-Powered Personal Stylist & Wardrobe Manager
"""

import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone


User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    """
    Custom JWT authentication backend
    """
    
    def authenticate(self, request):
        """
        Authenticate the user based on JWT token in Authorization header
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header:
            return None
        
        try:
            # Check if header starts with 'Bearer '
            if not auth_header.startswith('Bearer '):
                return None
            
            # Extract token
            token = auth_header.split(' ')[1]
            
            # Decode and validate token
            payload = self.decode_token(token)
            user = self.get_user_from_payload(payload)
            
            return (user, token)
            
        except (IndexError, jwt.InvalidTokenError, User.DoesNotExist):
            raise AuthenticationFailed('Invalid token')
    
    def decode_token(self, token):
        """
        Decode JWT token and validate
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # Check if token has expired
            if payload.get('exp', 0) < timezone.now().timestamp():
                raise AuthenticationFailed('Token has expired')
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
    
    def get_user_from_payload(self, payload):
        """
        Get user from token payload
        """
        try:
            user_id = payload.get('user_id')
            if not user_id:
                raise AuthenticationFailed('Invalid token payload')
            
            user = User.objects.get(user_id=user_id)
            
            # Check if user is active
            if not user.is_active:
                raise AuthenticationFailed('User account is inactive')
            
            # Check if account is locked
            if user.is_account_locked:
                raise AuthenticationFailed('User account is locked')
            
            # Check if email is verified
            if not user.email_verified:
                raise AuthenticationFailed('Email not verified')
            
            return user
            
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')


class TokenManager:
    """
    Utility class for generating and managing JWT tokens
    """
    
    @staticmethod
    def generate_access_token(user):
        """
        Generate access token for user
        """
        now = timezone.now()
        payload = {
            'user_id': str(user.user_id),
            'email': user.email,
            'name': user.name,
            'iat': now.timestamp(),
            'exp': (now + timedelta(seconds=settings.JWT_ACCESS_TOKEN_LIFETIME)).timestamp(),
            'type': 'access'
        }
        
        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
    
    @staticmethod
    def generate_refresh_token(user):
        """
        Generate refresh token for user
        """
        now = timezone.now()
        payload = {
            'user_id': str(user.user_id),
            'iat': now.timestamp(),
            'exp': (now + timedelta(seconds=settings.JWT_REFRESH_TOKEN_LIFETIME)).timestamp(),
            'type': 'refresh'
        }
        
        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
    
    @staticmethod
    def generate_activation_token(user):
        """
        Generate email activation token
        """
        now = timezone.now()
        payload = {
            'user_id': str(user.user_id),
            'email': user.email,
            'iat': now.timestamp(),
            'exp': (now + timedelta(seconds=settings.EMAIL_ACTIVATION_TOKEN_LIFETIME)).timestamp(),
            'type': 'activation'
        }
        
        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
    
    @staticmethod
    def generate_password_reset_token(user):
        """
        Generate password reset token
        """
        now = timezone.now()
        payload = {
            'user_id': str(user.user_id),
            'email': user.email,
            'iat': now.timestamp(),
            'exp': (now + timedelta(seconds=settings.PASSWORD_RESET_TOKEN_LIFETIME)).timestamp(),
            'type': 'password_reset'
        }
        
        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
    
    @staticmethod
    def decode_token(token, expected_type=None):
        """
        Decode any JWT token and validate
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # Check token type if specified
            if expected_type and payload.get('type') != expected_type:
                raise jwt.InvalidTokenError('Invalid token type')
            
            # Check if token has expired
            if payload.get('exp', 0) < timezone.now().timestamp():
                raise jwt.ExpiredSignatureError('Token has expired')
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError('Token has expired')
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError('Invalid token')
    
    @staticmethod
    def refresh_access_token(refresh_token):
        """
        Generate new access token from refresh token
        """
        try:
            payload = TokenManager.decode_token(refresh_token, 'refresh')
            user = User.objects.get(user_id=payload['user_id'])
            
            # Check user status
            if not user.is_active or user.is_account_locked or not user.email_verified:
                raise jwt.InvalidTokenError('User account is not valid')
            
            return TokenManager.generate_access_token(user)
            
        except (User.DoesNotExist, jwt.InvalidTokenError):
            raise jwt.InvalidTokenError('Invalid refresh token')
