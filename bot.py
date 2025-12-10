import os
import asyncio

from vkbottle import Bot

from start import classes
from rules import ConfigRule
from database import Database
from cachemanager import CacheManager

# Вставьте ваш токен или используйте os.getenv("TOKEN")
TOKEN = "vk1.a.5zh0zqg8PFXdRPC3XGo34ikkLt63VSqPu17iyZ-yH4BRYAeNExOstRLcsxj69qwEOyON6dpRwXaBOAJLYkVYsfyY-4cYEhOwvOy60WMquEYsHNbtY2YJt5t_vJCvDEEjGWjnGSqehhc98w306hJYFZCbhZkVYnBioDRdqWeb0xZNkEu7QuUwIF-HRD8FshXE0JdqSmJ81Qz_LPWRCy84ZQ"
DB_PATH = "eco_bot.db"

bot = Bot(token=TOKEN)


def setup_labelers():
    # Импорт обработчиков
    from handlers import general, map_service, gamification

    # Подключаем модули с логикой
    bot.labeler.load(general.bl)
    bot.labeler.load(map_service.bl)
    bot.labeler.load(gamification.bl)


async def startup_task(cache: CacheManager):
    """Действия при запуске бота"""
    print("🚀 Запуск Эко-бота...")
    await cache.get_data_from_db()


async def shutdown_task(cache: CacheManager):
    """Действия при остановке"""
    print("💤 Отключение...")
    if await cache.save_data_to_db():
        print('Всё успешно сохранилось в бд!')
    else:
        print('Что-то не сохранилось в бд!')


if __name__ == "__main__":
    bot.labeler.vbml_ignore_case = True

    # Создаём ключевые классы
    db = Database(DB_PATH)
    cache = CacheManager(db)

    classes.update_classes(db, cache, bot)

    # Создаём экземпляры ключевых классов
    bot.labeler.custom_rules['config'] = ConfigRule

    setup_labelers()

    # Регистрируем хуки запуска/остановки лупа
    bot.loop_wrapper.on_startup.append(startup_task(classes.cache))
    bot.loop_wrapper.on_shutdown.append(shutdown_task(classes.cache))

    # Запуск поллинга
    bot.run_forever()