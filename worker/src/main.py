import asyncio
import json
import logging
import os
from typing import Any, Dict

import aio_pika
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_users_db, get_backend_db
from src.repositories.user_repository import UserRepository
from src.repositories.article_repository import ArticleRepository

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="[%(asctime)s] [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

async def handle_message(message: aio_pika.IncomingMessage) -> None:
    async with message.process(requeue=True):
        payload: Dict[str, Any] = json.loads(message.body.decode("utf-8"))
        logger.info("Получено событие из очереди: %s", payload)

        author_id = payload.get("author_id")
        article_id = payload.get("post_id")

        # Получение списка подписчиков автора
        async for users_session in get_users_db():
            subscriber_ids = await UserRepository.get_subscribers_by_author_id(users_session, author_id)
            # Получить их subscription_key
            subs_keys = await UserRepository.get_users_subscription_keys_by_ids(users_session, subscriber_ids)

        # Получение title статьи
        async for backend_session in get_backend_db():
            article_title = await ArticleRepository.get_title_by_article_id(backend_session, article_id)

        msg_text = f"Новая статья '{article_title}' от автора {author_id}"
        if not subscriber_ids:
            logger.info("Нет подписчиков для автора %s", author_id)
            return

        async with httpx.AsyncClient() as client:
            for subscriber_id in subscriber_ids:
                try:
                    push_data = {
                        "subscriber_id": str(subscriber_id),
                        "message": msg_text
                    }
                    subscription_key = subs_keys.get(subscriber_id)
                    response = await client.post(
                        settings.push_notificator_url,
                        json=push_data,
                        timeout=10.0,
                        headers={"Authorization": f"Bearer {subscription_key}"}
                    )
                    response.raise_for_status()
                    logger.info("push sent to %s: %s", subscriber_id, msg_text)
                except Exception as exc:
                    logger.exception("Ошибка при отправке уведомления %s: %s", subscriber_id, exc)
                    continue

async def main() -> None:
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    queue = await channel.declare_queue(settings.post_queue_name, durable=True)
    await queue.consume(handle_message)
    logger.info("Ожидаю сообщения из очереди '%s'", settings.post_queue_name)
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

