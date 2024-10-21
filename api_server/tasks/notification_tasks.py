from celery import Celery
from aiogram import Bot
import asyncio

from api_server.config import settings


celery = Celery(
    "notifications",
    broker=settings.redis_url,
    broker_connection_retry_on_startup=True,
)


@celery.task
def send_notification_to_user(
        tg_chat_id: int,
        message: str,
        from_user: str
) -> None:
    bot = Bot(token=settings.BOT_TOKEN)
    asyncio.run(send_message(
        bot=bot,
        tg_chat_id=tg_chat_id,
        message=message,
        from_user=from_user
    ))


async def send_message(
        bot: Bot,
        tg_chat_id: int,
        message: str,
        from_user: str
) -> None:
    message = (f"Пропущенное сообщение от пользователя {from_user}.\n"
               f"\n"
               f'"{message}"')
    await bot.send_message(
        chat_id=tg_chat_id,
        text=message,
    )
