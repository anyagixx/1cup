# FILE: backend/app/cache/redis_client.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Redis caching layer for API responses
#   SCOPE: Cache get/set/delete, pub/sub for WebSocket events
#   DEPENDS: M-BE-CORE (config)
#   LINKS: M-BE-CACHE
# END_MODULE_CONTRACT

import json
from typing import Optional, Any
from datetime import timedelta
import redis.asyncio as redis

from app.config import get_settings

settings = get_settings()


class RedisClient:
    def __init__(self, url: Optional[str] = None):
        self.url = url or settings.redis_url
        self._client: Optional[redis.Redis] = None
        self._pubsub: Optional[redis.client.PubSub] = None
    
    async def connect(self) -> None:
        if self._client is None:
            self._client = redis.from_url(self.url, decode_responses=True)
    
    async def disconnect(self) -> None:
        if self._pubsub:
            await self._pubsub.close()
            self._pubsub = None
        if self._client:
            await self._client.close()
            self._client = None
    
    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            raise RuntimeError("Redis client not connected")
        return self._client
    
    async def get(self, key: str) -> Optional[Any]:
        value = await self.client.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        ttl = ttl or settings.redis_cache_ttl
        await self.client.setex(key, ttl, value)
        return True
    
    async def delete(self, key: str) -> bool:
        result = await self.client.delete(key)
        return result > 0
    
    async def delete_pattern(self, pattern: str) -> int:
        keys = await self.client.keys(pattern)
        if keys:
            return await self.client.delete(*keys)
        return 0
    
    async def publish(self, channel: str, message: dict) -> None:
        await self.client.publish(channel, json.dumps(message))
    
    async def subscribe(self, channel: str) -> redis.client.PubSub:
        if self._pubsub is None:
            self._pubsub = self.client.pubsub()
        await self._pubsub.subscribe(channel)
        return self._pubsub
    
    async def unsubscribe(self, channel: str) -> None:
        if self._pubsub:
            await self._pubsub.unsubscribe(channel)


redis_client = RedisClient()


async def get_redis() -> RedisClient:
    if redis_client._client is None:
        await redis_client.connect()
    return redis_client


async def cache_get(key: str) -> Optional[Any]:
    return await redis_client.get(key)


async def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    return await redis_client.set(key, value, ttl)


async def cache_delete(key: str) -> bool:
    return await redis_client.delete(key)
