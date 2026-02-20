import redis
import json
from flask import current_app

_redis_client = None


def get_redis():
    """get redis client (singleton)"""
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.from_url(
