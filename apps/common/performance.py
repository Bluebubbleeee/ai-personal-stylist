"""
Performance optimization utilities for AI-Powered Personal Stylist & Wardrobe Manager
"""

from django.core.cache import cache
from django.db import models
from django.conf import settings
from functools import wraps
import hashlib
import logging
import time
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate a cache key from arguments"""
    key_parts = [str(prefix)]
    
    # Add positional arguments
    for arg in args:
        if hasattr(arg, 'pk'):
            key_parts.append(f"{arg.__class__.__name__}:{arg.pk}")
        else:
            key_parts.append(str(arg))
    
    # Add keyword arguments
    for k, v in sorted(kwargs.items()):
        if hasattr(v, 'pk'):
            key_parts.append(f"{k}:{v.__class__.__name__}:{v.pk}")
        else:
            key_parts.append(f"{k}:{v}")
    
    # Create hash for long keys
    key_string = ":".join(key_parts)
    if len(key_string) > 240:  # Redis key limit is 250
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    return key_string


def cached_result(timeout: int = 300, key_prefix: str = "cached"):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_str = cache_key(f"{key_prefix}:{func.__name__}", *args, **kwargs)
            
            # Try to get from cache
            result = cache.get(cache_key_str)
            if result is not None:
                logger.debug(f"Cache hit for {cache_key_str}")
                return result
            
            # Execute function and cache result
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Cache the result
            cache.set(cache_key_str, result, timeout)
            
            logger.debug(f"Cached result for {cache_key_str} (execution: {execution_time:.2f}s)")
            return result
        
        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    """Invalidate cache keys matching a pattern"""
    try:
        # This would work with Redis backend
        from django.core.cache import cache
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern(pattern)
        else:
            # Fallback: clear specific known keys
            logger.warning(f"Cache backend doesn't support pattern deletion: {pattern}")
    except Exception as e:
        logger.error(f"Error invalidating cache pattern {pattern}: {str(e)}")


class QueryOptimizer:
    """Query optimization utilities"""
    
    @staticmethod
    def optimize_wardrobe_query(queryset):
        """Optimize wardrobe item queries"""
        return queryset.select_related('user').prefetch_related(
            'tags',
            models.Prefetch('tags', queryset=models.query.QuerySet(model=None).select_related())
        )
    
    @staticmethod
    def optimize_recommendation_query(queryset):
        """Optimize recommendation queries"""
        return queryset.select_related('user', 'session').prefetch_related(
            'items__tags',
            'items__user'
        )
    


class PerformanceMonitor:
    """Monitor and log performance metrics"""
    
    @staticmethod
    def log_query_performance(func):
        """Decorator to log database query performance"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            from django.db import connection
            
            queries_before = len(connection.queries)
            start_time = time.time()
            
            result = func(*args, **kwargs)
            
            execution_time = time.time() - start_time
            queries_after = len(connection.queries)
            query_count = queries_after - queries_before
            
            if query_count > 10 or execution_time > 1.0:
                logger.warning(
                    f"Performance warning for {func.__name__}: "
                    f"{query_count} queries, {execution_time:.2f}s"
                )
            else:
                logger.debug(
                    f"Performance: {func.__name__}: "
                    f"{query_count} queries, {execution_time:.2f}s"
                )
            
            return result
        return wrapper


# Performance-optimized query managers
class OptimizedQuerySet(models.QuerySet):
    """Base optimized queryset with common performance improvements"""
    
    def with_prefetch(self, *prefetch_lookups):
        """Add prefetch_related with performance monitoring"""
        return self.prefetch_related(*prefetch_lookups)
    
    def with_select(self, *select_lookups):
        """Add select_related with performance monitoring"""
        return self.select_related(*select_lookups)
    
    def cached(self, timeout=300, key_prefix="qs"):
        """Cache queryset results"""
        cache_key_str = cache_key(key_prefix, str(self.query))
        
        cached_result = cache.get(cache_key_str)
        if cached_result is not None:
            return cached_result
        
        result = list(self)
        cache.set(cache_key_str, result, timeout)
        return result


# Pagination optimization
def optimize_pagination(queryset, page_size=20):
    """Optimize pagination for large datasets"""
    if queryset.count() > 1000:
        # Use cursor-based pagination for large datasets
        return queryset.order_by('-created_at')[:page_size * 2]
    return queryset


# Database connection optimization
def optimize_db_queries():
    """Apply database connection optimizations"""
    from django.db import connection
    
    # Connection pooling would be configured at the database level
    # This is a placeholder for connection optimization logic
    cursor = connection.cursor()
    
    # Example: Set connection-level optimizations
    if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
        cursor.execute("SET work_mem = '256MB';")
        cursor.execute("SET maintenance_work_mem = '512MB';")
    
    cursor.close()


# Image optimization utilities
def optimize_image_processing():
    """Configure optimal image processing settings"""
    try:
        from PIL import Image
        
        # Set optimal thumbnail sizes
        THUMBNAIL_SIZES = {
            'small': (150, 150),
            'medium': (300, 300),
            'large': (600, 600)
        }
        
        # Configure image optimization settings
        Image.MAX_IMAGE_PIXELS = 89478485  # ~300MB limit
        
        return THUMBNAIL_SIZES
    except ImportError:
        logger.warning("Pillow not available for image optimization")
        return {}


# Static file optimization
STATIC_FILE_OPTIMIZATION = {
    'CSS_MINIFY': True,
    'JS_MINIFY': True,
    'GZIP_COMPRESSION': True,
    'CACHE_HEADERS': {
        'max-age': 31536000,  # 1 year
        'public': True
    }
}


# API response optimization
def optimize_api_response(data: Dict) -> Dict:
    """Optimize API response data"""
    # Remove null values to reduce payload size
    def remove_nulls(obj):
        if isinstance(obj, dict):
            return {k: remove_nulls(v) for k, v in obj.items() if v is not None}
        elif isinstance(obj, list):
            return [remove_nulls(item) for item in obj]
        return obj
    
    return remove_nulls(data)


# Memory optimization
def optimize_memory_usage():
    """Configure memory optimization settings"""
    import gc
    
    # Configure garbage collection
    gc.set_threshold(700, 10, 10)  # More aggressive GC
    
    # Clear unnecessary caches periodically
    cache.clear()
    
    logger.info("Memory optimization applied")


# Performance middleware configuration
PERFORMANCE_MIDDLEWARE_SETTINGS = {
    'GZIP_COMPRESSION': True,
    'CACHE_MIDDLEWARE': True,
    'SLOW_QUERY_THRESHOLD': 1.0,  # seconds
    'ENABLE_QUERY_PROFILING': settings.DEBUG,
    'MAX_QUERIES_PER_REQUEST': 50
}
