from vk_api.keyboard import VkKeyboard, VkKeyboardColor


class Keyboards:
    """Класс для создания клавиатур ВК"""

    @staticmethod
    def get_main_keyboard():
        """Создает главную клавиатуру"""
        keyboard = VkKeyboard(one_time=False)

        # Первый ряд
        keyboard.add_button('🗺️ Пункты приёма', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('📅 События', color=VkKeyboardColor.PRIMARY)

        # Второй ряд
        keyboard.add_line()
        keyboard.add_button('🌿 Советы', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('🏆 Рейтинг', color=VkKeyboardColor.SECONDARY)

        # Третий ряд
        keyboard.add_line()
        keyboard.add_button('👤 Профиль', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('💬 Отзыв', color=VkKeyboardColor.SECONDARY)

        # Четвертый ряд
        keyboard.add_line()
        keyboard.add_button('⚙️ Настройки', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('📋 Помощь', color=VkKeyboardColor.SECONDARY)

        return keyboard.get_keyboard()

    @staticmethod
    def get_cancel_keyboard():
        """Клавиатура для отмены действий"""
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('❌ Отмена', color=VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()

    @staticmethod
    def get_profile_keyboard():
        """Клавиатура для профиля"""
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('🔄 Обновить', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('🏠 Главная', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('✏️ Изменить город', color=VkKeyboardColor.SECONDARY)
        return keyboard.get_keyboard()

    @staticmethod
    def get_settings_keyboard():
        """Клавиатура настроек"""
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('📍 Изменить город', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('🔔 Уведомления', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('🎯 Мои интересы', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('🏠 Главная', color=VkKeyboardColor.SECONDARY)
        return keyboard.get_keyboard()

    @staticmethod
    def get_yes_no_keyboard():
        """Клавиатура Да/Нет"""
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('✅ Да', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('❌ Нет', color=VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()