"""
Simple in-memory cache for goal extractions and market data
"""
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class SimpleCache:
    """In-memory cache with TTL"""
    
    def __init__(self, ttl_seconds: int = None):
        self.cache: Dict[str, Any] = {}
        self.ttl = timedelta(seconds=ttl_seconds or settings.CACHE_TTL_SECONDS)
    
    def _generate_key(self, *args) -> str:
        """Generate cache key from arguments"""
        content = ":".join(str(arg) for arg in args)
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, *args) -> Optional[Any]:
        """Get cached value if available and not expired"""
        key = self._generate_key(*args)
        
        if key in self.cache:
            entry = self.cache[key]
            if datetime.utcnow() < entry["expires_at"]:
                logger.debug(f"Cache hit for key: {key[:8]}...")
                return entry["data"]
            else:
                # Expired, remove it
                del self.cache[key]
                logger.debug(f"Cache expired for key: {key[:8]}...")
        
        return None
    
    def set(self, *args, data: Any) -> None:
        """Cache value with TTL"""
        key = self._generate_key(*args)
        self.cache[key] = {
            "data": data,
            "expires_at": datetime.utcnow() + self.ttl,
            "cached_at": datetime.utcnow()
        }
        logger.debug(f"Cached data for key: {key[:8]}...")
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count"""
        now = datetime.utcnow()
        expired_keys = [
            k for k, v in self.cache.items()
            if now >= v["expires_at"]
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        now = datetime.utcnow()
        active = sum(1 for v in self.cache.values() if now < v["expires_at"])
        expired = len(self.cache) - active
        
        return {
            "total_entries": len(self.cache),
            "active_entries": active,
            "expired_entries": expired,
            "ttl_seconds": self.ttl.total_seconds()
        }

# Global cache instances
goal_extraction_cache = SimpleCache(ttl_seconds=3600)  # 1 hour for extractions
market_data_cache = SimpleCache(ttl_seconds=86400)     # 24 hours for market data