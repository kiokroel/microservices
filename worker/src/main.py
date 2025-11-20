import asyncio
import json
import logging
import os
from typing import Any, Dict
from uuid import UUID

import aio_pika
import httpx
from pydantic import BaseModel, ValidationError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.core.config import settings
from src.core.database import get_backend_db, get_users_db, get_worker_db
from src.repositories.article_repository import ArticleRepository
from src.repositories.notification_repository import NotificationRepository
from src.repositories.user_repository import UserRepository


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="[%(asctime)s] [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


class ArticlePublishedEvent(BaseModel):
    author_id: UUID
    post_id: UUID


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
    subscriber_id: UUID,
    author_id: UUID,
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


async def process_notification(
    *,
    semaphore: asyncio.Semaphore,
    client: httpx.AsyncClient,
    subscriber_id: UUID,
    author_id: UUID,
    article_id: UUID,
    msg_text: str,
    subscription_key: str,
    job_id: str | None,
) -> None:
    job_label = job_id or ""

    async with semaphore:
        async for worker_session in get_worker_db():
            notification_repo = NotificationRepository(worker_session)

            already_sent = await notification_repo.was_sent(
                subscriber_id=subscriber_id,
                post_id=article_id,
            )
            if already_sent:
                logger.info(
                    "job_id=%s author_id=%s subscriber_id=%s: push уже был отправлен, пропускаем",
                    job_label,
                    author_id,
                    subscriber_id,
                )
                return

            try:
                await send_push_with_retry(
                    client,
                    subscriber_id=subscriber_id,
                    author_id=author_id,
                    msg_text=msg_text,
                    subscription_key=subscription_key,
                    job_id=job_label,
                )
                await notification_repo.mark_sent(
                    subscriber_id=subscriber_id,
                    post_id=article_id,
                )
            except Exception as exc:
                logger.exception(
                    "job_id=%s author_id=%s subscriber_id=%s: "
                    "ошибка при отправке уведомления: %s",
                    job_label,
                    author_id,
                    subscriber_id,
                    exc,
                )
            return


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

        concurrency = max(settings.worker_concurrency, 1)
        semaphore = asyncio.Semaphore(concurrency)
        tasks = []

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

                tasks.append(
                    asyncio.create_task(
                        process_notification(
                            semaphore=semaphore,
                            client=client,
                            subscriber_id=subscriber_id,
                            author_id=author_id,
                            article_id=article_id,
                            msg_text=msg_text,
                            subscription_key=subscription_key,
                            job_id=str(job_id) if job_id is not None else "",
                        )
                    )
                )

            if tasks:
                await asyncio.gather(*tasks)


async def main() -> None:
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    queue = await channel.declare_queue(settings.post_queue_name, durable=True)
    await queue.consume(handle_message)
    logger.info("Ожидаю сообщения из очереди '%s'", settings.post_queue_name)
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
