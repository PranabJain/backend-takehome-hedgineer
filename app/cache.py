import json
from typing import Any, Optional

import redis

from .config import settings


class Cache:
    def __init__(self) -> None:
        self.enabled = settings.redis_enabled
        self.client: Optional[redis.Redis] = None
        if self.enabled:
            try:
                self.client = redis.from_url(settings.redis_url, decode_responses=True)
                self.client.ping()
            except Exception:
                self.client = None
                self.enabled = False

    def get_json(self, key: str) -> Optional[Any]:
        if not (self.enabled and self.client):
            return None
        data = self.client.get(key)
        if data is None:
            return None
        return json.loads(data)

    def set_json(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        if not (self.enabled and self.client):
            return
        self.client.setex(key, ttl_seconds, json.dumps(value))


cache = Cache()

