import os 
import redis.asyncio as redis


valkey = redis.from_url(os.getenv("VALKEY_URL"), decode_responses=True)
