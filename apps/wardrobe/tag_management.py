"""
Tag Management System for AI-Powered Personal Stylist & Wardrobe Manager
Handles tag normalization, suggestions, and bulk operations
"""

import logging
from django.db.models import Count, Q
from typing import List, Dict, Set, Tuple
import re
from collections import defaultdict

from .models import Tag, CanonicalTag, ClothingItem

logger = logging.getLogger(__name__)


class TagManager:
    """Comprehensive tag management system"""
    
    def __init__(self):
        # Synonyms mapping for tag normalization
        self.synonyms = {
            'casual': ['relaxed', 'informal', 'everyday', 'comfortable'],
            'formal': ['dress', 'dressy', 'elegant', 'professional'],
            'vintage': ['retro', 'classic', 'old-fashioned', 'antique'],
            'modern': ['contemporary', 'current', 'trendy', 'fashionable'],
            'comfortable': ['comfy', 'cozy', 'soft', 'easy-wear'],
            'summer': ['warm-weather', 'hot', 'sunny'],
            'winter': ['cold-weather', 'warm', 'cozy'],
            'sporty': ['athletic', 'active', 'fitness', 'gym'],
            'party': ['festive', 'celebration', 'event', 'night-out'],
            'work': ['office', 'business', 'professional', 'corporate'],
        }
        
        # Common tag categories
        self.tag_categories = {
            'style': ['casual', 'formal', 'vintage', 'modern', 'sporty', 'bohemian', 'minimalist'],
            'occasion': ['work', 'party', 'date', 'wedding', 'vacation', 'everyday'],
            'season': ['summer', 'winter', 'spring', 'fall', 'all-season'],
            'material': ['cotton', 'silk', 'wool', 'denim', 'leather', 'polyester'],
            'pattern': ['striped', 'floral', 'solid', 'plaid', 'polka-dot', 'geometric'],
            'fit': ['tight', 'loose', 'fitted', 'oversized', 'regular'],
            'comfort': ['comfortable', 'breathable', 'stretchy', 'soft'],
        }
    
    def normalize_tag(self, tag_name: str) -> str:
        """Normalize a tag name to its canonical form"""
        if not tag_name or not isinstance(tag_name, str):
            return ""
        
        # Clean the tag
        cleaned = tag_name.lower().strip()
        cleaned = re.sub(r'[^\w\s-]', '', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Check for synonyms
        for canonical, synonyms in self.synonyms.items():
            if cleaned in synonyms or cleaned == canonical:
                return canonical
        
        # Return cleaned version
        return cleaned
    
    def suggest_tags(self, user, context: Dict = None) -> List[str]:
        """Suggest tags for a clothing item based on context and user history"""
        suggestions = []
        
        try:
            # Get user's most used tags
            user_tags = Tag.objects.filter(
                item__user=user
            ).values('tag').annotate(
                count=Count('tag')
            ).order_by('-count')[:20]
            
            popular_tags = [tag['tag'] for tag in user_tags]
            
            # Add context-based suggestions
            if context:
                category = context.get('category')
                color = context.get('color')
                season = context.get('season')
                
                # Category-based suggestions
                category_suggestions = self._get_category_suggestions(category)
                suggestions.extend(category_suggestions)
                
                # Color-based suggestions
                if color:
                    suggestions.append(color)
                
                # Season-based suggestions
                if season and season != 'all_season':
                    suggestions.append(season)
            
            # Add popular user tags (if not already included)
            for tag in popular_tags[:10]:
                if tag not in suggestions:
                    suggestions.append(tag)
            
            # Add general popular tags
            general_tags = self._get_general_popular_tags()
            for tag in general_tags:
                if tag not in suggestions and len(suggestions) < 15:
                    suggestions.append(tag)
            
            return suggestions[:12]  # Limit to 12 suggestions
            
        except Exception as e:
            logger.error(f"Error generating tag suggestions: {str(e)}")
            return []
    
    def _get_category_suggestions(self, category: str) -> List[str]:
        """Get tag suggestions based on clothing category"""
        suggestions = {
            'tops': ['casual', 'formal', 'comfortable', 'work', 'everyday'],
            'bottoms': ['casual', 'formal', 'comfortable', 'denim', 'work'],
            'dresses': ['formal', 'party', 'date', 'elegant', 'occasion'],
            'shoes': ['casual', 'formal', 'comfortable', 'athletic', 'everyday'],
            'outerwear': ['warm', 'winter', 'layering', 'casual', 'formal'],
            'accessories': ['statement', 'subtle', 'formal', 'casual', 'everyday'],
            'activewear': ['sporty', 'athletic', 'comfortable', 'gym', 'fitness'],
            'sleepwear': ['comfortable', 'soft', 'cozy', 'relaxed'],
        }
        
        return suggestions.get(category, ['casual', 'comfortable'])
    
    def _get_general_popular_tags(self) -> List[str]:
        """Get generally popular tags across all users"""
        try:
            popular = Tag.objects.values('tag').annotate(
                count=Count('tag')
            ).order_by('-count')[:20]
            
            return [tag['tag'] for tag in popular]
        except Exception:
            # Fallback to common tags
            return ['casual', 'comfortable', 'formal', 'everyday', 'work', 'party']
    
    def bulk_update_tags(self, user, operations: List[Dict]) -> Dict:
        """Perform bulk tag operations"""
        results = {
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            for operation in operations:
                op_type = operation.get('type')  # 'add', 'remove', 'replace', 'normalize'
                item_ids = operation.get('item_ids', [])
                tags = operation.get('tags', [])
                
                if op_type == 'add':
                    results.update(self._bulk_add_tags(user, item_ids, tags))
                elif op_type == 'remove':
                    results.update(self._bulk_remove_tags(user, item_ids, tags))
                elif op_type == 'replace':
                    old_tag = operation.get('old_tag')
                    new_tag = operation.get('new_tag')
                    results.update(self._bulk_replace_tag(user, old_tag, new_tag))
                elif op_type == 'normalize':
                    results.update(self._bulk_normalize_tags(user, item_ids))
                
        except Exception as e:
            logger.error(f"Error in bulk tag operations: {str(e)}")
            results['errors'].append(str(e))
        
        return results
    
    def _bulk_add_tags(self, user, item_ids: List[str], tags: List[str]) -> Dict:
        """Add tags to multiple items"""
        success = 0
        failed = 0
        
        try:
            items = ClothingItem.objects.filter(
                item_id__in=item_ids,
                user=user
            )
            
            for item in items:
                try:
                    for tag_name in tags:
                        normalized_tag = self.normalize_tag(tag_name)
                        if normalized_tag:
                            Tag.objects.get_or_create(
                                item=item,
                                tag=normalized_tag,
                                defaults={'source': 'user'}
                            )
                    success += 1
                except Exception as e:
                    logger.error(f"Error adding tags to item {item.item_id}: {str(e)}")
                    failed += 1
            
        except Exception as e:
            logger.error(f"Error in bulk add tags: {str(e)}")
            failed += len(item_ids)
        
        return {'success': success, 'failed': failed}
    
    def _bulk_remove_tags(self, user, item_ids: List[str], tags: List[str]) -> Dict:
        """Remove tags from multiple items"""
        success = 0
        failed = 0
        
        try:
            normalized_tags = [self.normalize_tag(tag) for tag in tags]
            
            deleted_count = Tag.objects.filter(
                item__item_id__in=item_ids,
                item__user=user,
                tag__in=normalized_tags
            ).delete()[0]
            
            success = deleted_count
            
        except Exception as e:
            logger.error(f"Error in bulk remove tags: {str(e)}")
            failed = len(item_ids)
        
        return {'success': success, 'failed': failed}
    
    def _bulk_replace_tag(self, user, old_tag: str, new_tag: str) -> Dict:
        """Replace all instances of one tag with another"""
        success = 0
        failed = 0
        
        try:
            old_normalized = self.normalize_tag(old_tag)
            new_normalized = self.normalize_tag(new_tag)
            
            if not old_normalized or not new_normalized:
                return {'success': 0, 'failed': 1}
            
            # Find all tags to replace
            tags_to_replace = Tag.objects.filter(
                item__user=user,
                tag=old_normalized
            )
            
            for tag in tags_to_replace:
                try:
                    # Check if new tag already exists for this item
                    existing = Tag.objects.filter(
                        item=tag.item,
                        tag=new_normalized
                    ).first()
                    
                    if existing:
                        # Delete old tag
                        tag.delete()
                    else:
                        # Update old tag
                        tag.tag = new_normalized
                        tag.save()
                    
                    success += 1
                    
                except Exception as e:
                    logger.error(f"Error replacing tag for item {tag.item.item_id}: {str(e)}")
                    failed += 1
            
        except Exception as e:
            logger.error(f"Error in bulk replace tag: {str(e)}")
            failed = 1
        
        return {'success': success, 'failed': failed}
    
    def _bulk_normalize_tags(self, user, item_ids: List[str]) -> Dict:
        """Normalize tags for multiple items"""
        success = 0
        failed = 0
        
        try:
            items = ClothingItem.objects.filter(
                item_id__in=item_ids,
                user=user
            ).prefetch_related('tags')
            
            for item in items:
                try:
                    tags = list(item.tags.all())
                    updated = False
                    
                    for tag in tags:
                        normalized = self.normalize_tag(tag.tag)
                        if normalized != tag.tag:
                            # Check if normalized version already exists
                            existing = Tag.objects.filter(
                                item=item,
                                tag=normalized
                            ).first()
                            
                            if existing:
                                # Delete old tag
                                tag.delete()
                            else:
                                # Update tag
                                tag.tag = normalized
                                tag.save()
                            
                            updated = True
                    
                    if updated:
                        success += 1
                        
                except Exception as e:
                    logger.error(f"Error normalizing tags for item {item.item_id}: {str(e)}")
                    failed += 1
            
        except Exception as e:
            logger.error(f"Error in bulk normalize tags: {str(e)}")
            failed = len(item_ids)
        
        return {'success': success, 'failed': failed}
    
    def get_tag_analytics(self, user) -> Dict:
        """Get tag usage analytics for user"""
        try:
            # Most used tags
            most_used = Tag.objects.filter(
                item__user=user
            ).values('tag').annotate(
                count=Count('tag')
            ).order_by('-count')[:10]
            
            # Tag sources breakdown
            sources = Tag.objects.filter(
                item__user=user
            ).values('source').annotate(
                count=Count('source')
            )
            
            # Tags by category
            user_items = ClothingItem.objects.filter(user=user)
            category_tags = defaultdict(list)
            
            for item in user_items:
                for tag in item.tags.all():
                    category_tags[item.category].append(tag.tag)
            
            # Clean up category data
            category_summary = {}
            for category, tag_list in category_tags.items():
                tag_counts = defaultdict(int)
                for tag in tag_list:
                    tag_counts[tag] += 1
                
                # Get top 5 tags for this category
                top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                category_summary[category] = top_tags
            
            return {
                'most_used_tags': list(most_used),
                'tag_sources': list(sources),
                'tags_by_category': category_summary,
                'total_tags': Tag.objects.filter(item__user=user).count(),
                'unique_tags': Tag.objects.filter(item__user=user).values('tag').distinct().count()
            }
            
        except Exception as e:
            logger.error(f"Error getting tag analytics: {str(e)}")
            return {}
    
    def cleanup_unused_tags(self, user) -> int:
        """Remove tags that are no longer associated with any items"""
        try:
            # This is handled by Django's cascade delete, but we can add additional cleanup logic here
            deleted_count = 0
            
            # Find orphaned canonical tags (if any)
            orphaned_canonical = CanonicalTag.objects.filter(
                is_active=True
            ).annotate(
                usage_count=Count('tag_set')
            ).filter(usage_count=0)
            
            for canonical in orphaned_canonical:
                if canonical.created_at < timezone.now() - timedelta(days=30):
                    canonical.is_active = False
                    canonical.save()
                    deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up tags: {str(e)}")
            return 0


# Global tag manager instance
tag_manager = TagManager()


def normalize_tag(tag_name: str) -> str:
    """Convenience function to normalize a tag"""
    return tag_manager.normalize_tag(tag_name)


def suggest_tags(user, context: Dict = None) -> List[str]:
    """Convenience function to get tag suggestions"""
    return tag_manager.suggest_tags(user, context)


def bulk_update_tags(user, operations: List[Dict]) -> Dict:
    """Convenience function for bulk tag operations"""
    return tag_manager.bulk_update_tags(user, operations)
