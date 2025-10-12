"""
Simple in-memory cache for Football API responses
Prevents exceeding rate limits (10 requests/min)
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import threading


class SimpleCache:
    """Thread-safe in-memory cache"""
    
    def __init__(self, ttl_seconds: int = 300):  # 5 minutes default TTL
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                if datetime.now() < entry['expires']:
                    print(f"📦 Cache HIT: {key}")
                    return entry['value']
                else:
                    print(f"⏰ Cache EXPIRED: {key}")
                    del self.cache[key]
        
        print(f"❌ Cache MISS: {key}")
        return None
    
    def set(self, key: str, value: Any):
        """Store value in cache with TTL"""
        with self.lock:
            self.cache[key] = {
                'value': value,
                'expires': datetime.now() + timedelta(seconds=self.ttl),
                'cached_at': datetime.now()
            }
            print(f"💾 Cached: {key} (TTL: {self.ttl}s)")
    
    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            count = len(self.cache)
            self.cache.clear()
            print(f"🗑️  Cleared {count} cache entries")
    
    def cleanup_expired(self):
        """Remove expired entries"""
        with self.lock:
            now = datetime.now()
            expired = [k for k, v in self.cache.items() if now >= v['expires']]
            for key in expired:
                del self.cache[key]
            if expired:
                print(f"🧹 Cleaned up {len(expired)} expired entries")


# Global cache instance for Football API
# TTL = 5 minutes to respect rate limits while providing fresh data
football_cache = SimpleCache(ttl_seconds=300)
