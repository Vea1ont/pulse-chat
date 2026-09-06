import json

from aiokafka import AIOKafkaProducer

producer = AIOKafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda v: json.dumps(v).encode(),
)


async def publish_user_deleted(user_id: int):
    await producer.send_and_wait(
        "user-events", {"event": "user.deleted", "user_id": user_id}
    )
