import os
import redis
import logging

from dataclasses import dataclass
from opentelemetry import trace

tracer = trace.get_tracer("otel-python-app")

logger = logging.getLogger(__name__)

@dataclass
class RedisConfig(object):
    def __init__(self):
        self.url = os.environ.get("REDIS_URL", None)
        self.host = self.url.split(":")[1]
        self.port = self.url.split(":")[2].split("/")[0]
        self.db = self.url.split('/')[3]


class RedisClient:
    def __init__(self, config: RedisConfig = None):
        if config is None:
            config = RedisConfig()
        self.config = config
        self.client = redis.from_url(url=self.config.url)

    def get_dict(self, key: str) -> {}:
        return self.client.hgetall(key)

    def set_key(self, key: str, value: str) -> None:
        self.client.set(key, value)
        return None

    def set_dict(self, key: str, value: dict) -> None:
        self.client.hmset(key, value)
        return None

    def delete_key(self, key):
        self.client.delete(key)
        return None


@tracer.start_as_current_span("get-redis-client")
def get_redis_client(config: RedisConfig) -> redis.Redis:
    try:
        return redis.from_url(url=config.url)
    except Exception as e:
        raise f'CONNECTION FAILED: {e}: {config.url}'


@tracer.start_as_current_span("redis-status")
def redis_status() -> dict:
    config = RedisConfig()
    r = get_redis_client(config)
    status = {
        "status": "OK",
        "url": config.url,
        "port": config.port,
        "db": config.db,
    }

    if not r.ping():
        status['status'] = 'FAILED'

    return status


