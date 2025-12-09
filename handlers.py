import logging
import random
from vk_api.utils import get_random_id
from database import SimpleDatabase
from keyboards import Keyboards
from config import config

logger = logging.getLogger(__name__)


class MessageHandler:
    """Обработчик входящих сообщений"""

    def __init__(self, vk_api):
        self.vk_api = vk_api
        self.db = SimpleDatabase()
        self.commands = self._get_commands_list()

    def _get_commands_list(self):
        """Возвращает список всех команд"""
        return {
            'start': 'Начать работу с ботом',
            'help': 'Показать список команд',
            'profile': 'Мой профиль и статистика',
            'points': 'Пункты приёма вторсырья',
            'events': 'Ближайшие эко-события',
            'tips': 'Случайный эко-совет',
            'rating': 'Рейтинг активности',
            'feedback': 'Оставить отзыв о боте',
            'settings': 'Настройки бота',
            'город [название]': 'Указать свой город'
        }

    def send_message(self, user_id, text, keyboard=None):
        """Отправляет сообщение пользователю"""
        params = {
            'user_id': user_id,
            'message': text,
            'random_id': get_random_id(),
        }

        if keyboard:
            params['keyboard'] = keyboard
        else:
            params['keyboard'] = Keyboards.get_main_keyboard()

        try:
            self.vk_api.messages.send(**params)
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            return False

    def handle_message(self, user_id, message, first_name="", last_name=""):
        """Основной метод обработки сообщения"""
        message_lower = message.lower().strip()

        # Обработка команд
        if message_lower in ['привет', 'start', 'начать', 'старт', 'hello', 'hi']:
            return self._handle_start(user_id, first_name)
        elif message_lower in ['помощь', 'help', 'команды', 'справка']:
            return self._handle_help(user_id)
        elif message_lower in ['профиль', 'profile', 'статистика', 'мой профиль']:
            return self._handle_profile(user_id)
        elif 'пункт' in message_lower or 'points' in message_lower or 'приём' in message_lower:
            return self._handle_points(user_id)
        elif 'события' in message_lower or 'events' in message_lower or 'мероприятия' in message_lower:
            return self._handle_events(user_id)
        elif 'совет' in message_lower or 'tips' in message_lower or 'подсказка' in message_lower:
            return self._handle_tips(user_id)
        elif 'рейтинг' in message_lower or 'rating' in message_lower or 'топ' in message_lower:
            return self._handle_rating(user_id)
        elif 'отзыв' in message_lower or 'feedback' in message_lower:
            return self._handle_feedback(user_id, message)
        elif 'город' in message_lower:
            return self._handle_city(user_id, message)
        elif 'настройки' in message_lower or 'settings' in message_lower:
            return self._handle_settings(user_id)
        elif message_lower in ['спасибо', 'thanks', 'благодарю']:
            return self._handle_thanks(user_id)
        elif message_lower in ['о боте', 'about', 'информация']:
            return self._handle_about(user_id)

        # Если команда не распознана
        return self._handle_unknown(user_id, message)

    def _handle_start(self, user_id, first_name):
        """Обработка приветствия"""
        user = self.db.get_or_create_user(user_id, first_name, "")

        welcome_text = (
            f"Привет, {first_name}! 👋\n\n"
            f"Я - {config.BOT_NAME} ({config.BOT_VERSION})\n\n"
            f"Я помогу тебе:\n"
            f"• Найти ближайшие пункты приёма вторсырья ♻️\n"
            f"• Узнать об эко-событиях в твоём городе 🌿\n"
            f"• Получить полезные советы по снижению эко-следа\n"
            f"• Отслеживать твою эко-активность\n\n"
            f"Используй меню ниже или напиши команду!\n"
            f"Начни с 'помощь' чтобы увидеть все возможности."
        )

        # Добавляем баллы за начало работы
        self.db.add_user_action(user_id, 'start', 5, "Начал работу с ботом")

        self.send_message(user_id, welcome_text)
        return {'success': True, 'action': 'start'}

    def _handle_help(self, user_id):
        """Показывает список команд"""
        help_text = "📋 *Доступные команды:*\n\n"

        for cmd, desc in self.commands.items():
            help_text += f"• *{cmd}* - {desc}\n"

        help_text += "\n*Примеры использования:*\n"
        help_text += "`город Москва` - указать город\n"
        help_text += "`отзыв Отличный бот!` - оставить отзыв\n"
        help_text += "`совет` - получить эко-совет\n\n"
        help_text += "Или используй кнопки меню ниже! 👇"

        self.send_message(user_id, help_text)
        return {'success': True, 'action': 'help'}

    def _handle_profile(self, user_id):
        """Показывает профиль пользователя"""
        user = self.db.get_or_create_user(user_id, "", "")
        stats = self.db.get_user_stats(user_id)

        if not stats:
            self.send_message(user_id, "❌ Ошибка загрузки профиля")
            return {'success': False, 'action': 'profile_error'}

        profile_text = (
            f"👤 *Твой профиль:*\n\n"
            f"*Имя:* {user['first_name']} {user.get('last_name', '')}\n"
            f"*Город:* {user['city'] or 'не указан'}\n"
            f"*Эко-рейтинг:* {stats['score']} баллов\n"
            f"*Уровень:* {stats['level']}\n"
            f"*Просмотрено советов:* {stats['tips_viewed']}\n"
            f"*Выполнено действий:* {stats['actions_count']}\n"
            f"*Зарегистрирован:* {stats['registration_date']}\n\n"
            f"Чтобы изменить город, напиши: `город Москва`\n"
            f"или нажми 'Изменить город' в меню ниже."
        )

        self.send_message(user_id, profile_text, Keyboards.get_profile_keyboard())
        return {'success': True, 'action': 'profile'}

    def _handle_points(self, user_id):
        """Поиск пунктов приёма"""
        user = self.db.get_or_create_user(user_id, "", "")
        city = user['city'] or 'твоем городе'

        # Получаем пункты приема для города или дефолтные
        if city in config.RECYCLING_POINTS:
            points = config.RECYCLING_POINTS[city]
        else:
            points = config.RECYCLING_POINTS['default']

        points_text = f"🗺️ *Пункты приёма в {city}:*\n\n"

        for i, point in enumerate(points, 1):
            points_text += f"{i}. {point}\n"

        points_text += "\n*Совет:* Уточни город для более точной информации!\n"
        points_text += "Напиши: `город Москва`"

        # Добавляем баллы за поиск
        self.db.add_user_action(user_id, 'search_points', 3, "Искал пункты приема")

        self.send_message(user_id, points_text)
        return {'success': True, 'action': 'points_search'}

    def _handle_events(self, user_id):
        """Показывает ближайшие эко-события"""
        events_text = "📅 *Ближайшие эко-события:*\n\n"

        for i, event in enumerate(config.ECO_EVENTS[:5], 1):
            events_text += f"{i}. {event}\n"

        user = self.db.get_or_create_user(user_id, "", "")
        if user['city']:
            events_text += f"\n*В твоём городе ({user['city']}) скоро:*\n"
            events_text += "🔜 Информация о локальных событиях появится позже!\n"

        events_text += "\n*Укажи город для точных событий:*\n"
        events_text += "Напиши: `город Москва`"

        # Добавляем баллы
        self.db.add_user_action(user_id, 'view_events', 2, "Смотрел события")

        self.send_message(user_id, events_text)
        return {'success': True, 'action': 'events_list'}

    def _handle_tips(self, user_id):
        """Даёт случайный эко-совет"""
        tip = random.choice(config.ECO_TIPS)
        user = self.db.get_or_create_user(user_id, "", "")

        # Обновляем статистику
        user['tips_viewed'] += 1
        self.db.add_user_action(user_id, 'view_tip', 5, "Посмотрел эко-совет")

        tips_text = (
            f"🌿 *Эко-совет дня:*\n\n"
            f"{tip}\n\n"
            f"+5 баллов к рейтингу! 🎉\n"
            f"*Просмотрено советов:* {user['tips_viewed']}\n\n"
            f"Пиши `совет` для нового совета!\n"
            f"Каждый совет делает планету чище! 🌍"
        )

        self.send_message(user_id, tips_text)
        return {'success': True, 'action': 'daily_tip'}

    def _handle_rating(self, user_id):
        """Показывает рейтинг активности"""
        user = self.db.get_or_create_user(user_id, "", "")
        top_users = self.db.get_top_users(limit=10)

        rating_text = "🏆 *Топ эко-активистов:*\n\n"

        for i, top_user in enumerate(top_users, 1):
            name = top_user['first_name'][:10] if top_user['first_name'] else f"User{top_user['vk_id']}"
            city = f" ({top_user['city']})" if top_user['city'] else ""
            highlight = "➡️ " if top_user['vk_id'] == user_id else ""
            rating_text += f"{i}. {highlight}*{name}*{city}: {top_user['eco_score']} баллов\n"

        # Находим позицию текущего пользователя
        user_position = None
        for i, top_user in enumerate(top_users, 1):
            if top_user['vk_id'] == user_id:
                user_position = i
                break

        if user_position:
            rating_text += f"\n*Твоя позиция:* {user_position}\n"
        else:
            rating_text += f"\n*Твои баллы:* {user['eco_score']}\n"

        rating_text += f"*Твой уровень:* {user['level']}\n\n"
        rating_text += "Зарабатывай баллы:\n• Смотри советы (+5)\n• Указывай город (+10)\n• Оставляй отзывы (+15)"

        self.send_message(user_id, rating_text)
        return {'success': True, 'action': 'rating_view'}

    def _handle_feedback(self, user_id, message):
        """Обработка отзывов"""
        feedback_text = message.replace('отзыв', '', 1).replace('feedback', '', 1).strip()

        if not feedback_text:
            feedback_text = "💬 *Чтобы оставить отзыв:*\n\n"
            feedback_text += "1. Напиши `отзыв` и через пробел свой текст\n"
            feedback_text += "2. Например: `отзыв Отличный бот, помог найти пункт приёма!`\n\n"
            feedback_text += "Твой отзыв поможет нам стать лучше! 💚"

            self.send_message(user_id, feedback_text)
            return {'success': True, 'action': 'feedback_info'}

        # Сохраняем отзыв
        self.db.add_feedback(user_id, feedback_text)
        self.db.add_user_action(user_id, 'leave_feedback', 15, "Оставил отзыв")

        response_text = (
            f"✅ *Спасибо за отзыв!* +15 баллов! 🌟\n\n"
            f"Мы учтём твоё мнение:\n"
            f"`{feedback_text[:100]}{'...' if len(feedback_text) > 100 else ''}`\n\n"
            f"Твой вклад в развитие эко-сообщества очень важен! 💚"
        )

        self.send_message(user_id, response_text)
        return {'success': True, 'action': 'feedback_submitted'}

    def _handle_city(self, user_id, message):
        """Обработка установки города"""
        city_name = message.replace('город', '', 1).strip()

        if not city_name:
            self.send_message(
                user_id,
                "📍 *Укажи название города:*\n\n"
                "Напиши: `город Москва`\n"
                "или `город Санкт-Петербург`\n\n"
                "Это поможет давать точные рекомендации!"
            )
            return {'success': False, 'action': 'city_empty'}

        # Обновляем город
        self.db.update_user_city(user_id, city_name)

        response_text = (
            f"✅ *Город установлен:* {city_name}\n"
            f"+10 баллов к рейтингу! 🌟\n\n"
            f"Теперь я могу:\n"
            f"• Показывать ближайшие пункты приёма\n"
            f"• Информировать о местных событиях\n"
            f"• Давать актуальные рекомендации\n\n"
            f"Попробуй команду `пункты` или `события`!"
        )

        self.send_message(user_id, response_text)
        return {'success': True, 'action': 'city_set'}

    def _handle_settings(self, user_id):
        """Настройки бота"""
        settings_text = (
            f"⚙️ *Настройки бота:*\n\n"
            f"*Доступные опции:*\n"
            f"• Изменить город\n"
            f"• Настроить уведомления\n"
            f"• Выбрать интересы\n"
            f"• О боте и версия\n\n"
            f"Используй меню ниже или команды:\n"
            f"`город [название]` - изменить город\n"
            f"`о боте` - информация о боте"
        )

        self.send_message(user_id, settings_text, Keyboards.get_settings_keyboard())
        return {'success': True, 'action': 'settings'}

    def _handle_thanks(self, user_id):
        """Обработка благодарности"""
        thanks_text = (
            "🙏 *Спасибо тебе!*\n\n"
            "Твоя экологическая осознанность вдохновляет!\n"
            "Каждое маленькое действие имеет значение.\n\n"
            "Продолжай в том же духе! 💚🌍"
        )

        self.send_message(user_id, thanks_text)
        return {'success': True, 'action': 'thanks'}

    def _handle_about(self, user_id):
        """Информация о боте"""
        about_text = (
            f"🤖 *{config.BOT_NAME}*\n\n"
            f"*Версия:* {config.BOT_VERSION}\n"
            f"*Режим:* Тестовый (без базы данных)\n\n"
            f"*Цель проекта:*\n"
            f"Повышение экологической грамотности и помощь в сортировке отходов.\n\n"
            f"*Возможности:*\n"
            f"• Поиск пунктов приёма вторсырья\n"
            f"• Информация об эко-событиях\n"
            f"• Персональные эко-советы\n"
            f"• Система рейтинга и мотивации\n\n"
            f"*Технологии:*\n"
            f"• Python + VK API\n"
            f"• Хранение данных в памяти\n"
            f"• Готов к интеграциям (карты, БД, уведомления)\n\n"
            f"Спасибо, что помогаешь делать мир чище! 💚"
        )

        self.send_message(user_id, about_text)
        return {'success': True, 'action': 'about'}

    def _handle_unknown(self, user_id, message):
        """Обработка неизвестной команды"""
        unknown_text = (
            f"🤔 *Не понял команду:* `{message[:50]}{'...' if len(message) > 50 else ''}`\n\n"
            f"*Доступные команды:*\n"
            f"• `помощь` - все команды\n"
            f"• `профиль` - твоя статистика\n"
            f"• `город Москва` - указать город\n"
            f"• `совет` - эко-совет дня\n"
            f"• `отзыв текст` - оставить отзыв\n\n"
            f"Или используй кнопки меню ниже! 👇"
        )

        self.send_message(user_id, unknown_text)
        return {'success': False, 'action': 'unknown_command'}