import asyncio
import json
import logging
import os
from typing import Any, Dict

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx
import aio_pika
from pydantic import BaseModel, ValidationError, Field
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


class ArticlePublishedEvent(BaseModel):
    author_id: int = Field(..., gt=0)
    post_id: int = Field(..., gt=0)


NETWORK_EXCEPTIONS = (
    httpx.TimeoutException,
    httpx.ConnectError,
    httpx.NetworkError,
)


@retry(
    retry=retry_if_exception_type(NETWORK_EXCEPTIONS),
    stop=stop_after_attempt(3),  # 3 попытки
    wait=wait_exponential(multiplier=1, min=1, max=5),  # 1s, 2s, 4s
    reraise=True,
)
async def send_push_with_retry(
    client: httpx.AsyncClient,
    *,
    subscriber_id: int,
    author_id: int,
    msg_text: str,
    subscription_key: str,
    job_id: str | None,
) -> None:
    push_data = {
        "subscriber_id": str(subscriber_id),
        "message": msg_text,
    }

    response = await client.post(
        settings.push_notificator_url,
        json=push_data,
        timeout=httpx.Timeout(5.0, connect=2.0),
        headers={"Authorization": f"Bearer {subscription_key}"},
    )
    response.raise_for_status()
    logger.info(
        "job_id=%s author_id=%s subscriber_id=%s: push sent",
        job_id,
        author_id,
        subscriber_id,
    )


async def handle_message(message: aio_pika.IncomingMessage) -> None:
    async with message.process(requeue=True):
        job_id = getattr(message, "message_id", None)

        try:
            raw = message.body.decode("utf-8")
            raw_payload: Dict[str, Any] = json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.error(
                "job_id=%s: некорректный JSON, сообщение будет отклонено: %s",
                job_id,
                exc,
            )
            await message.reject(requeue=False)
            return

        try:
            event = ArticlePublishedEvent.model_validate(raw_payload)
        except ValidationError as exc:
            logger.error(
                "job_id=%s: невалидный payload, сообщение будет отклонено: %s",
                job_id,
                exc,
            )
            await message.reject(requeue=False)
            return

        author_id = event.author_id
        article_id = event.post_id

        logger.info(
            "job_id=%s: валидное событие из очереди: author_id=%s post_id=%s",
            job_id,
            author_id,
            article_id,
        )

        # Получение списка подписчиков автора
        async for users_session in get_users_db():
            subscriber_ids = await UserRepository.get_subscribers_by_author_id(
                users_session, author_id
            )
            subs_keys = await UserRepository.get_users_subscription_keys_by_ids(
                users_session, subscriber_ids
            )

        # Получение title статьи
        async for backend_session in get_backend_db():
            article_title = await ArticleRepository.get_title_by_article_id(
                backend_session, article_id
            )

        msg_text = f"Новая статья '{article_title}' от автора {author_id}"
        if not subscriber_ids:
            logger.info("job_id=%s: нет подписчиков для автора %s", job_id, author_id)
            return

        async with httpx.AsyncClient() as client:
            for subscriber_id in subscriber_ids:
                subscription_key = subs_keys.get(subscriber_id)
                if not subscription_key:
                    logger.warning(
                        "job_id=%s author_id=%s subscriber_id=%s: нет subscription_key",
                        job_id,
                        author_id,
                        subscriber_id,
                    )
                    continue

                try:
                    await send_push_with_retry(
                        client,
                        subscriber_id=subscriber_id,
                        author_id=author_id,
                        msg_text=msg_text,
                        subscription_key=subscription_key,
                        job_id=str(job_id) if job_id is not None else "",
                    )
                except Exception as exc:
                    logger.exception(
                        "job_id=%s author_id=%s subscriber_id=%s: "
                        "ошибка при отправке уведомления: %s",
                        job_id,
                        author_id,
                        subscriber_id,
                        exc,
                    )
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
