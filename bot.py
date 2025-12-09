import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
import logging
from datetime import datetime

from config import config
from database_test import Database
from handlers.commands import CommandHandler
from keyboards.main_menu import MainMenuKeyboard

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EcoBot:
    def __init__(self):
        self.vk_session = vk_api.VkApi(token=config.VK_TOKEN)
        self.vk_api = self.vk_session.get_api()
        self.longpoll = VkLongPoll(self.vk_session)
        self.db = Database()

        logger.info("Бот инициализирован")

    def send_message(self, user_id, text, keyboard=None):
        """Отправка сообщения пользователю"""
        params = {
            'user_id': user_id,
            'message': text,
            'random_id': get_random_id(),
            'dont_parse_links': 1
        }

        if keyboard:
            params['keyboard'] = keyboard

        try:
            self.vk_api.messages.send(**params)
            logger.debug(f"Отправлено сообщение пользователю {user_id}")
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")

    def handle_message(self, user_id, message, first_name="", last_name=""):
        """Обработка входящего сообщения"""
        try:
            # Создаем обработчик команд
            handler = CommandHandler(self.vk_api, self.db, user_id)

            # Обрабатываем сообщение
            result = handler.handle(
                message,
                first_name=first_name,
                last_name=last_name
            )

            logger.info(f"Обработано сообщение от {user_id}: {message}")
            return result

        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")

            # Отправляем сообщение об ошибке
            self.send_message(
                user_id,
                "😔 Произошла ошибка при обработке сообщения. Попробуйте позже.",
                MainMenuKeyboard().get_keyboard()
            )

            return {'success': False, 'error': str(e)}

    def run(self):
        """Запуск основного цикла бота"""
        logger.info("Запуск бота...")

        for event in self.longpoll.listen():
            try:
                # Новое сообщение
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    user_id = event.user_id
                    message = event.text.strip()

                    logger.info(f"Новое сообщение от {user_id}: {message}")

                    # Получаем информацию о пользователе
                    user_info = self.vk_api.users.get(user_ids=user_id)[0]
                    first_name = user_info.get('first_name', '')
                    last_name = user_info.get('last_name', '')

                    # Обрабатываем сообщение
                    self.handle_message(user_id, message, first_name, last_name)

                # Другие типы событий можно добавить здесь

            except Exception as e:
                logger.error(f"Ошибка в основном цикле: {e}")


def main():
    # Проверяем наличие токена
    if not config.VK_TOKEN:
        logger.error("Токен ВК не найден! Укажите его в переменной окружения VK_TOKEN")
        return

    # Создаем и запускаем бота
    bot = EcoBot()
    bot.run()


if __name__ == "__main__":
    main()