import json

import sentry_sdk
from aiokafka import AIOKafkaConsumer
from cache import valkey


async def chat_cache_invalidation():
    consumer = AIOKafkaConsumer(
        "user-events",
        bootstrap_servers="kafka:9092",
        group_id="chat-cache-invalidator",
        value_deserializer=lambda v: json.loads(v.decode()),
        enable_auto_commit=False,  # отключаем авто движение
        # "закладки" на следующее  событие. Т.к. если упадет
        # консьюмер где-то по середине, то могут быть потери
    )

    await consumer.start()
    try:  # внешний try — гарантирует stop() при остановке сервиса
        async for msg in consumer:
            try:  # внутренний try — ловит ошибку ОДНОГО сообщения,
                # чтобы битое событие не убило весь цикл
                data = msg.value
                # print(data, flush=True)
                if data["event"] == "user.deleted":
                    user_id = data["user_id"]
                    keys = await valkey.keys(f"user:{user_id}:chats:*")
                    blacklist_key = f"blacklist:user:{user_id}"
                    if keys:
                        await valkey.delete(*keys)
                        # print(keys, flush=True)

                    await valkey.set(blacklist_key, "1", ex=86400)

            except Exception as e:
                print(
                    f"[consumer] ошибка: {e} | partition={msg.partition} "
                    f"offset={msg.offset} value={msg.value}",
                    flush=True,
                )
                sentry_sdk.capture_exception(e)

            # коммитим в любом случае: и после успеха, и после ошибки.
            # Иначе битое сообщение читалось бы вечно и заблокировало
            # обработку всех следующих
            await consumer.commit()

    finally:
        await consumer.stop()
