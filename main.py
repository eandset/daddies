from vkbottle import Bot
import asyncio
import logging

from database.database import Database
from cachemanager.cachemanager import CacheManager
from handlers.users import setup_users


logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(
        token="ваш_токен"
    )

    db = Database()
    cache = CacheManager(db)

    await cache.get_data_from_db()

    setup_users(bot)

    try:
        await bot.run_polling()
    except KeyboardInterrupt:
        print("\nБот остановлен")
    finally:
        await cache.save_data_to_db()


if __name__ == "__main__":
    asyncio.run(main())