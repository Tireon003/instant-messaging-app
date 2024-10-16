from aiogram import Bot, Dispatcher
import asyncio
import logging

from config import settings
from routers import activation_router

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

dp.include_router(activation_router)


async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
