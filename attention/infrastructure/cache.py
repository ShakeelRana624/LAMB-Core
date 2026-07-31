"""
Redis cache integration for the Attention Engine.

This module provides caching for expensive computations
to improve performance and reduce latency.
"""

from typing import Optional, Any, Dict
import json
import hashlib

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class RedisCache:
    """
    Redis cache for attention computations.
    
    Caches expensive computations like novelty and goal relevance
    to improve performance and reduce latency.
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        ttl_seconds: int = 300,
        enable_cache: bool = True,
    ):
        """
        Initialize the Redis cache.
        
        Args:
            redis_url: Redis connection URL
            ttl_seconds: Time-to-live for cached items
            enable_cache: Whether to enable caching
        """
        self.redis_url = redis_url
        self.ttl_seconds = ttl_seconds
        self.enable_cache = enable_cache and REDIS_AVAILABLE
        self._client: Optional[redis.Redis] = None
        
        if self.enable_cache:
            self._connect()
    
    def _connect(self) -> None:
        """Connect to Redis."""
        try:
            self._client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
            # Test connection
            self._client.ping()
        except Exception as e:
            print(f"[Attention] Redis connection failed: {e}. Disabling cache.")
            self.enable_cache = False
            self._client = None
    
    def _generate_key(
        self,
        signal_name: str,
        input_text: str,
        context: Dict[str, Any],
    ) -> str:
        """
        Generate a cache key.
        
        Args:
            signal_name: Name of the signal
            input_text: Input text
            context: Additional context
            
        Returns:
            Cache key
        """
        # Create a deterministic key from inputs
        key_data = f"{signal_name}:{input_text}:{json.dumps(context, sort_keys=True)}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"attention:{signal_name}:{key_hash}"
    
    def get(
        self,
        signal_name: str,
        input_text: str,
        context: Dict[str, Any],
    ) -> Optional[Any]:
        """
        Get cached value.
        
        Args:
            signal_name: Name of the signal
            input_text: Input text
            context: Additional context
            
        Returns:
            Cached value, or None if not found
        """
        if not self.enable_cache or not self._client:
            return None
        
        try:
            key = self._generate_key(signal_name, input_text, context)
            value = self._client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None
    
    def set(
        self,
        signal_name: str,
        input_text: str,
        context: Dict[str, Any],
        value: Any,
    ) -> bool:
        """
        Set cached value.
        
        Args:
            signal_name: Name of the signal
            input_text: Input text
            context: Additional context
            value: Value to cache
            
        Returns:
            True if successful
        """
        if not self.enable_cache or not self._client:
            return False
        
        try:
            key = self._generate_key(signal_name, input_text, context)
            serialized = json.dumps(value)
            self._client.setex(key, self.ttl_seconds, serialized)
            return True
        except Exception:
            return False
    
    def delete(
        self,
        signal_name: str,
        input_text: str,
        context: Dict[str, Any],
    ) -> bool:
        """
        Delete cached value.
        
        Args:
            signal_name: Name of the signal
            input_text: Input text
            context: Additional context
            
        Returns:
            True if successful
        """
        if not self.enable_cache or not self._client:
            return False
        
        try:
            key = self._generate_key(signal_name, input_text, context)
            self._client.delete(key)
            return True
        except Exception:
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching a pattern.
        
        Args:
            pattern: Redis key pattern
            
        Returns:
            Number of keys deleted
        """
        if not self.enable_cache or not self._client:
            return 0
        
        try:
            keys = self._client.keys(pattern)
            if keys:
                return self._client.delete(*keys)
            return 0
        except Exception:
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        if not self.enable_cache or not self._client:
            return {
                "enabled": False,
                "connected": False,
            }
        
        try:
            info = self._client.info()
            return {
                "enabled": True,
                "connected": True,
                "ttl_seconds": self.ttl_seconds,
                "used_memory": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
            }
        except Exception:
            return {
                "enabled": True,
                "connected": False,
            }
