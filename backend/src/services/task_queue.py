import json
import logging
from typing import Optional
from uuid import UUID

import aio_pika
from aio_pika import DeliveryMode, Message
from aio_pika.abc import AbstractChannel

from src.core.config import settings

logger = logging.getLogger(__name__)

_connection: Optional[aio_pika.RobustConnection] = None
_channel: Optional[AbstractChannel] = None
_queue_declared: bool = False


async def _get_channel() -> AbstractChannel:
    """Создать (или переиспользовать) подключение и канал RabbitMQ."""
    global _connection, _channel, _queue_declared

    if not _connection or _connection.is_closed:
        _connection = await aio_pika.connect_robust(
            settings.queue_settings.rabbitmq_url
        )
        logger.info("Установлено соединение с RabbitMQ")

    if not _channel or _channel.is_closed:
        _channel = await _connection.channel()
        await _channel.set_qos(prefetch_count=10)
        _queue_declared = False

    if not _queue_declared:
        await _channel.declare_queue(
            settings.queue_settings.post_queue_name, durable=True
        )
        _queue_declared = True
        logger.info(
            "Очередь '%s' задекларирована",
            settings.queue_settings.post_queue_name,
        )

    return _channel


async def init_queue() -> None:
    """Явная инициализация соединения (вызывается при старте приложения)."""
    try:
        await _get_channel()
    except Exception:
        logger.exception("Не удалось инициализировать очередь RabbitMQ при старте")


async def close_queue() -> None:
    """Закрыть соединение/канал (для graceful shutdown)."""
    global _connection, _channel, _queue_declared
    try:
        if _channel and not _channel.is_closed:
            await _channel.close()
        if _connection and not _connection.is_closed:
            await _connection.close()
    finally:
        _channel = None
        _connection = None
        _queue_declared = False
        logger.info("Соединение с RabbitMQ закрыто")


async def enqueue_post_created(author_id: UUID | str, post_id: UUID | str) -> None:
    """Поставить задачу о создании поста в очередь RabbitMQ."""
    payload = {"author_id": str(author_id), "post_id": str(post_id)}
    channel = await _get_channel()
    message = Message(
        json.dumps(payload).encode("utf-8"),
        content_type="application/json",
        delivery_mode=DeliveryMode.PERSISTENT,
    )
    await channel.default_exchange.publish(
        message, routing_key=settings.queue_settings.post_queue_name
    )
    logger.info("Отправлено событие post_created: %s", payload)

