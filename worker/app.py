import asyncio
import json
import logging
import os
from typing import Any, Dict

import aio_pika
import httpx

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="[%(asctime)s] [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
POST_QUEUE_NAME = os.getenv("POST_QUEUE_NAME", "post_events")
PUSH_NOTIFICATOR_URL = os.getenv(
    "PUSH_NOTIFICATOR_URL", "http://push-notificator:8000/api/v1/notify"
)
PUSH_NOTIFICATION_TOKEN = os.getenv("PUSH_NOTIFICATION_TOKEN", "demo-token")


async def handle_message(message: aio_pika.IncomingMessage) -> None:
    async with message.process(requeue=True):
        payload: Dict[str, Any] = json.loads(message.body.decode("utf-8"))
        logger.info("Получено событие из очереди: %s", payload)
        msg_text = f"Новый пост {payload.get('post_id')} от автора {payload.get('author_id')}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    PUSH_NOTIFICATOR_URL,
                    headers={"Authorization": f"Bearer {PUSH_NOTIFICATION_TOKEN}"},
                    json={"message": msg_text},
                    timeout=10.0,
                )
                response.raise_for_status()
                logger.info(
                    "push-notificатор ответил %s, message='%s'",
                    response.status_code,
                    msg_text,
                )
            except Exception as exc:
                logger.exception("Ошибка при отправке уведомления: %s", exc)
                raise


async def main() -> None:
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue(POST_QUEUE_NAME, durable=True)
    await queue.consume(handle_message)
    logger.info("Ожидаю сообщения из очереди '%s'", POST_QUEUE_NAME)
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())

