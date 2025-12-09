import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import logging
import sys

from config import config
from handlers import MessageHandler

# Настройка логирования
logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class EcoBot:
    """Главный класс бота"""

    def __init__(self):
        # Проверяем наличие токена
        if not config.VK_TOKEN:
            logger.error("Токен VK не найден!")
            self._show_token_help()
            sys.exit(1)

        # Инициализируем VK API
        try:
            self.vk_session = vk_api.VkApi(token=config.VK_TOKEN)
            self.vk_api = self.vk_session.get_api()
            self.longpoll = VkLongPoll(self.vk_session)
            self.handler = MessageHandler(self.vk_api)

            logger.info(f"Бот инициализирован: {config.BOT_NAME}")
            logger.info(f"Токен: {config.VK_TOKEN[:10]}...")
        except Exception as e:
            logger.error(f"Ошибка инициализации VK API: {e}")
            sys.exit(1)

    def _show_token_help(self):
        """Показывает справку по получению токена"""
        print("\n" + "=" * 60)
        print("🚫 ТОКЕН VK НЕ НАЙДЕН!")
        print("=" * 60)
        print("\nЧтобы запустить бота, нужно:")
        print("\n1. Создать файл .env в папке с ботом со строкой:")
        print("   VK_TOKEN=ваш_токен_здесь")
        print("\n2. ИЛИ установить переменную окружения:")
        print("   export VK_TOKEN=ваш_токен_здесь")
        print("\n3. ИЛИ отредактировать config.py и раскомментировать строку:")
        print("   # VK_TOKEN = \"ваш_токен_здесь\"")
        print("\n4. Получить токен можно в настройках группы ВК:")
        print("   Управление → Работа с API → Ключи доступа")
        print("\nТребуемые права: messages, groups")
        print("=" * 60)

    def _show_welcome(self):
        """Показывает приветственное сообщение"""
        print("\n" + "=" * 60)
        print(f"🤖 {config.BOT_NAME}")
        print(f"📍 Версия: {config.BOT_VERSION}")
        print("=" * 60)
        print("\nДля работы бота необходимо:")
        print("1. ✅ Токен VK группы")
        print("2. ✅ Включенный LongPoll API в настройках группы")
        print("3. ✅ Разрешение на отправку сообщений")
        print("\nСостояние:")
        print(f"• Токен: {'✅ Установлен' if config.VK_TOKEN else '❌ Отсутствует'}")
        print(f"• Режим: {'🔧 Отладка' if config.DEBUG else '🚀 Продакшн'}")
        print("=" * 60)
        print("\nБот запущен! Ожидание сообщений...")
        print("Напишите 'привет' в личные сообщения группы")
        print("Для остановки нажмите Ctrl+C")
        print("=" * 60 + "\n")

    def run(self):
        """Запускает основной цикл бота"""
        self._show_welcome()

        logger.info("Запуск основного цикла обработки сообщений...")

        try:
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    self._process_message(event)
        except KeyboardInterrupt:
            logger.info("Бот остановлен пользователем")
            print("\n👋 Бот остановлен")
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
            print(f"\n❌ Критическая ошибка: {e}")

    def _process_message(self, event):
        """Обрабатывает входящее сообщение"""
        user_id = event.user_id
        message = event.text.strip()

        logger.info(f"Сообщение от {user_id}: {message}")

        try:
            # Получаем информацию о пользователе
            user_info = self.vk_api.users.get(user_ids=user_id, fields='city')[0]
            first_name = user_info.get('first_name', 'Пользователь')
            last_name = user_info.get('last_name', '')

            # Обрабатываем сообщение
            self.handler.handle_message(user_id, message, first_name, last_name)

        except vk_api.exceptions.ApiError as e:
            logger.error(f"Ошибка VK API: {e}")
            self.handler.send_message(
                user_id,
                "❌ Произошла ошибка при обработке запроса. Попробуйте позже."
            )
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")
            self.handler.send_message(
                user_id,
                "😔 Произошла внутренняя ошибка. Администратор уже уведомлен."
            )


def main():
    """Точка входа"""
    bot = EcoBot()
    bot.run()


if __name__ == "__main__":
    main()