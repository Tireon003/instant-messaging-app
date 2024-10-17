from celery import Celery
from aiogram import Bot

from api_server.config import settings


celery = Celery(
    "notifications",
    broker=settings.redis_url,
    broker_connection_retry_on_startup=True,
)


@celery.task
async def send_notification_to_user(tg_chat_id: int, message: str) -> None:
    bot = Bot(token=settings.BOT_TOKEN)
    await bot.send_message(
        chat_id=tg_chat_id,
        text=message,
    )
