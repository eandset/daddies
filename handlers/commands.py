from .base_handler import BaseHandler
from database_test.repository import UserRepository
from keyboards.main_menu import MainMenuKeyboard


class CommandHandler(BaseHandler):
    """Обработчик основных команд бота"""

    COMMANDS = {
        'start': 'Начать работу с ботом',
        'help': 'Показать список команд',
        'profile': 'Мой профиль',
        'points': 'Пункты приёма рядом',
        'events': 'Эко-события',
        'tips': 'Эко-советы',
        'rating': 'Рейтинг активности',
        'feedback': 'Оставить отзыв',
        'settings': 'Настройки'
    }

    async def handle(self, message: str, **kwargs):
        message_lower = message.lower().strip()

        if message_lower == 'привет' or message_lower == 'start' or message_lower == 'начать':
            return await self._handle_start()
        elif message_lower == 'help' or message_lower == 'помощь':
            return await self._handle_help()
        elif message_lower == 'profile' or message_lower == 'профиль':
            return await self._handle_profile()
        elif message_lower == 'points' or 'пункт' in message_lower:
            return await self._handle_points()
        elif message_lower == 'events' or 'события' in message_lower:
            return await self._handle_events()
        elif message_lower == 'tips' or 'совет' in message_lower:
            return await self._handle_tips()
        elif message_lower == 'rating' or 'рейтинг' in message_lower:
            return await self._handle_rating()
        elif 'отзыв' in message_lower or 'feedback' in message_lower:
            return await self._handle_feedback()
        elif 'настройки' in message_lower or 'settings' in message_lower:
            return await self._handle_settings()

        # Если команда не распознана
        return {
            'success': False,
            'message': 'Не понял команду. Используйте /help для списка команд',
            'keyboard': MainMenuKeyboard().get_keyboard()
        }

    async def _handle_start(self):
        """Обработка команды начала работы"""
        user_repo = UserRepository(self.db)
        user = user_repo.get_or_create_user(
            self.user_id,
            kwargs.get('first_name', ''),
            kwargs.get('last_name', '')
        )

        welcome_text = (
            f"Привет, {user.first_name}! 👋\n"
            f"Я - Экологический помощник!\n\n"
            f"Я помогу тебе:\n"
            f"• Найти ближайшие пункты приёма вторсырья ♻️\n"
            f"• Узнать об эко-событиях в твоём городе 🌿\n"
            f"• Получить персонализированные советы по снижению эко-следа\n"
            f"• Отслеживать твою эко-активность и соревноваться с другими\n\n"
            f"Используй меню ниже или напиши команду:"
        )

        self.send_message(welcome_text, MainMenuKeyboard())

        return {
            'success': True,
            'action': 'start',
            'user_id': self.user_id
        }

    async def _handle_help(self):
        """Показывает список всех команд"""
        help_text = "📋 Доступные команды:\n\n"
        for cmd, desc in self.COMMANDS.items():
            help_text += f"• {cmd} - {desc}\n"

        help_text += "\nТакже ты можешь использовать кнопки меню ниже!"

        self.send_message(help_text, MainMenuKeyboard())
        return {'success': True, 'action': 'help'}

    async def _handle_profile(self):
        """Показывает профиль пользователя"""
        user_repo = UserRepository(self.db)
        user = user_repo.get_or_create_user(self.user_id, '', '')

        profile_text = (
            f"👤 Твой профиль:\n"
            f"Имя: {user.first_name} {user.last_name}\n"
            f"Город: {user.city or 'не указан'}\n"
            f"Эко-рейтинг: {user.eco_score} баллов\n"
            f"Уровень: {user.level}\n"
            f"Зарегистрирован: {user.registration_date.strftime('%d.%m.%Y')}\n\n"
            f"Чтобы изменить город, напиши: 'город Москва'"
        )

        self.send_message(profile_text, MainMenuKeyboard())
        return {'success': True, 'action': 'profile'}

    async def _handle_points(self):
        """Поиск пунктов приёма (заглушка для интеграции с картами)"""
        self.send_message(
            "🗺️ Функция поиска пунктов приёма в разработке.\n"
            "Скоро здесь будет интеграция с картами!\n\n"
            "Пока что ты можешь:\n"
            "• Указать свой город: 'город Москва'\n"
            "• Посмотреть общие советы по сортировке",
            MainMenuKeyboard()
        )
        return {'success': True, 'action': 'points_search'}

    async def _handle_events(self):
        """Показывает ближайшие эко-события"""
        self.send_message(
            "📅 Функция эко-событий в разработке.\n"
            "Скоро здесь будут:\n"
            "• Список ближайших мероприятий\n"
            "• Возможность регистрации\n"
            "• Напоминания о событиях",
            MainMenuKeyboard()
        )
        return {'success': True, 'action': 'events_list'}

    async def _handle_tips(self):
        """Даёт случайный эко-совет"""
        tips = [
            "♻️ Используй многоразовые сумки вместо пластиковых пакетов",
            "💡 Выключай свет, выходя из комнаты",
            "🚰 Пей воду из многоразовой бутылки",
            "🚶 Передвигайся пешком или на велосипеде на короткие расстояния",
            "📱 Сдай старый телефон на переработку",
            "🍎 Планируй покупки, чтобы не выбрасывать еду"
        ]

        import random
        tip = random.choice(tips)

        self.send_message(
            f"🌿 Эко-совет дня:\n\n{tip}\n\n"
            f"Каждый день новый совет!",
            MainMenuKeyboard()
        )
        return {'success': True, 'action': 'daily_tip'}

    async def _handle_rating(self):
        """Показывает рейтинг активности"""
        self.send_message(
            "🏆 Система рейтинга в разработке.\n"
            "Скоро здесь будет:\n"
            "• Твой текущий рейтинг\n"
            "• Топ активных пользователей\n"
            "• Награды за достижения",
            MainMenuKeyboard()
        )
        return {'success': True, 'action': 'rating_view'}

    async def _handle_feedback(self):
        """Обработка отзывов"""
        self.send_message(
            "💬 Чтобы оставить отзыв:\n"
            "1. Напиши 'отзыв' и через пробел свой текст\n"
            "2. Например: 'отзыв Отличный бот, помог найти пункт приёма!'",
            MainMenuKeyboard()
        )
        return {'success': True, 'action': 'feedback_start'}

    async def _handle_settings(self):
        """Настройки бота"""
        self.send_message(
            "⚙️ Настройки бота:\n\n"
            "Доступные опции:\n"
            "• Указать город: 'город [название]'\n"
            "• Включить/выключить уведомления\n"
            "• Выбор интересов\n\n"
            "Что ты хочешь настроить?",
            MainMenuKeyboard()
        )
        return {'success': True, 'action': 'settings'}