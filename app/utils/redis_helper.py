import redis
from ..config.globals import settings

r = redis.from_url(f"{settings.REDIS_LOCATION}/10", decode_responses=True)
