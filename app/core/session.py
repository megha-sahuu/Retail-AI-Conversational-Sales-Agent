from typing import Dict, Any
import json
import redis
from .config import get_settings
from loguru import logger


class SessionStore:
    def __init__(self):
        settings = get_settings()
        try:
            self._redis = redis.from_url(settings.redis_url)
            self._redis.ping()
            self._use_redis = True
            logger.info("Using Redis session store")
        except Exception as exc:
            logger.warning(f"Redis unavailable, using in-memory store: {exc}")
            self._use_redis = False
            self._memory: Dict[str, Dict[str, Any]] = {}

    def _key(self, session_id: str) -> str:
        return f"session:{session_id}"

    def get(self, session_id: str) -> Dict[str, Any]:
        if self._use_redis:
            raw = self._redis.get(self._key(session_id))
            if raw:
                return json.loads(raw)
            return {}
        return self._memory.get(session_id, {})

    def set(self, session_id: str, data: Dict[str, Any]) -> None:
        if self._use_redis:
            self._redis.set(self._key(session_id), json.dumps(data), ex=60 * 60 * 12)
        else:
            self._memory[session_id] = data


session_store = SessionStore()
