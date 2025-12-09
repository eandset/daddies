import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
import logging
import sys
import json

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
        print("\n*Возможности геолокации:*")
        print("✅ Прием геолокации через скрепку 📎")
        print("✅ Поиск по адресу или названию места")
        print("✅ Обработка кодов геолокации ВК")
        print("✅ Интерактивные подсказки для пользователей")
        print("\n*Отладка:* Включен режим логирования вложений")
        print("=" * 60)
        print("\nБот запущен! Ожидание сообщений...")
        print("Пользователь может:")
        print("1. Написать 'где я' для поиска по геолокации")
        print("2. Отправить геолокацию через скрепку 📎")
        print("3. Написать адрес для поиска")
        print("=" * 60 + "\n")

    def send_message(self, user_id, text, keyboard=None, attachment=None):
        """Отправляет сообщение пользователю"""
        params = {
            'user_id': user_id,
            'message': text,
            'random_id': get_random_id(),
        }

        if keyboard:
            params['keyboard'] = keyboard

        if attachment:
            params['attachment'] = attachment

        try:
            self.vk_api.messages.send(**params)
            logger.debug(f"Отправлено сообщение пользователю {user_id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            return False

    def _parse_attachments(self, event):
        """Парсит вложения из события"""
        attachments = None

        try:
            # Получаем raw данные события
            event_dict = event.raw

            # Ищем вложения в разных форматах
            if 'attachments' in event_dict:
                attachments = event_dict['attachments']
            elif 'geo' in event_dict:
                attachments = {'geo': event_dict['geo']}

            # Логируем для отладки
            if attachments:
                logger.debug(f"Raw вложения из события: {attachments}")

        except Exception as e:
            logger.error(f"Ошибка парсинга вложений: {e}")

        return attachments

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

        # Парсим вложения
        attachments = self._parse_attachments(event)

        logger.info(f"Сообщение от {user_id}: '{message}', вложения: {attachments}")

        try:
            # Получаем информацию о пользователе
            user_info = self.vk_api.users.get(user_ids=user_id, fields='city')[0]
            first_name = user_info.get('first_name', 'Пользователь')
            last_name = user_info.get('last_name', '')

            # Обрабатываем сообщение через хендлер с вложениями
            self.handler.handle_message(
                user_id,
                message,
                first_name,
                last_name,
                attachments=attachments
            )

        except vk_api.exceptions.ApiError as e:
            logger.error(f"Ошибка VK API: {e}")
            self.send_message(
                user_id,
                "❌ Произошла ошибка при обработке запроса. Попробуйте позже."
            )
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")
            logger.exception("Подробности ошибки:")
            self.send_message(
                user_id,
                "😔 Произошла внутренняя ошибка. Администратор уже уведомлен."
            )


def main():
    """Точка входа"""
    bot = EcoBot()
    bot.run()


if __name__ == "__main__":
    main()