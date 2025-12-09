import os
import asyncio
from vkbottle import Bot
from database.db import db

# Импорт обработчиков
from handlers import general, map_service, gamification

# Вставьте ваш токен или используйте os.getenv("TOKEN")
TOKEN = "vk1.a.e0gXIlAOeoDFpNkkUrnZEu2ctKjZbAowpZd8JoToQmRMO_xEluC9p7zdLzoVgjgLt5eh-E5LUzpwz3URFmVk41MqKMAZdBcw2BGRB1ltlPFf6mf6DP-KQOmarnRhrCKJxvpoYG2nFafCkFYI-BIciHbltJ8vO9yLEgouBaO6qUR3XseSFyTL8BpSZTW-VHISXwdvPf3J_85QFHwATCmUng"

bot = Bot(token=TOKEN)


def setup_labelers():
    # Подключаем модули с логикой
    bot.labeler.load(general.bl)
    bot.labeler.load(map_service.bl)
    bot.labeler.load(gamification.bl)


async def startup_task():
    """Действия при запуске бота"""
    print("🚀 Запуск Эко-бота...")
    await db.connect()


async def shutdown_task():
    """Действия при остановке"""
    print("💤 Отключение...")
    await db.close()


if __name__ == "__main__":
    setup_labelers()

    # Регистрируем хуки запуска/остановки лупа
    bot.loop_wrapper.on_startup.append(startup_task())
    bot.loop_wrapper.on_shutdown.append(shutdown_task())

    # Запуск поллинга
    bot.run_forever()