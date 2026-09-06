from cache import valkey
from fastapi import HTTPException, Request


async def login_limit(request: Request):
    user_ip = request.client.host
    key = f"rate:login:{user_ip}"
    count = await valkey.incr(key)  # атомарное увалеичение числа на 1
    # и возврат результата

    if count == 1:
        await valkey.expire(key, 60)

    elif count > 5:
        raise HTTPException(429, "Too many requests")


async def register_limit(request: Request):
    user_ip = request.client.host
    key = f"rate:register:{user_ip}"
    count = await valkey.incr(key)

    if count == 1:
        await valkey.expire(key, 60)

    elif count > 5:
        raise HTTPException(429, "Too many requests")
