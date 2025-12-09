from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import json


class Keyboards:
    """Класс для создания клавиатур ВК"""

    @staticmethod
    def get_main_keyboard():
        """Создает главную клавиатуру"""
        keyboard = VkKeyboard(inline=False)

        # Первый ряд
        keyboard.add_button('📍 Где я?', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('🗺️ По городу', color=VkKeyboardColor.PRIMARY)

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
    def get_location_keyboard():
        """Клавиатура для запроса геолокации"""
        keyboard = VkKeyboard(one_time=True, inline=False)

        # Кнопка для отправки геолокации
        keyboard.add_button('📍 Отправить геолокацию', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('🏙️ Указать город', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('❌ Отмена', color=VkKeyboardColor.NEGATIVE)

        return keyboard.get_keyboard()

    @staticmethod
    def get_location_or_city_keyboard():
        """Клавиатура выбора способа поиска"""
        keyboard = VkKeyboard(one_time=True, inline=False)

        # Первый ряд
        keyboard.add_button('📍 По геолокации', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('🏙️ По городу', color=VkKeyboardColor.PRIMARY)

        # Второй ряд
        keyboard.add_line()
        keyboard.add_button('❌ Отмена', color=VkKeyboardColor.NEGATIVE)

        return keyboard.get_keyboard()

    @staticmethod
    def get_cancel_keyboard():
        """Клавиатура для отмены действий"""
        keyboard = VkKeyboard(one_time=True, inline=False)
        keyboard.add_button('❌ Отмена', color=VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()

    @staticmethod
    def get_profile_keyboard():
        """Клавиатура для профиля"""
        keyboard = VkKeyboard(inline=False)

        # Первый ряд
        keyboard.add_button('📍 Найти рядом', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('🏠 Главная', color=VkKeyboardColor.SECONDARY)

        # Второй ряд
        keyboard.add_line()
        keyboard.add_button('✏️ Изменить город', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('🔄 Обновить', color=VkKeyboardColor.SECONDARY)

        return keyboard.get_keyboard()

    @staticmethod
    def get_settings_keyboard():
        """Клавиатура настроек"""
        keyboard = VkKeyboard(inline=False)

        # Первый ряд
        keyboard.add_button('📍 Настроить поиск', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('🔔 Уведомления', color=VkKeyboardColor.PRIMARY)

        # Второй ряд
        keyboard.add_line()
        keyboard.add_button('🎯 Мои интересы', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('🏠 Главная', color=VkKeyboardColor.SECONDARY)

        return keyboard.get_keyboard()

    @staticmethod
    def get_yes_no_keyboard():
        """Клавиатура Да/Нет"""
        keyboard = VkKeyboard(one_time=True, inline=False)

        # Первый ряд
        keyboard.add_button('✅ Да', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('❌ Нет', color=VkKeyboardColor.NEGATIVE)

        return keyboard.get_keyboard()

    @staticmethod
    def get_simple_keyboard():
        """Простая клавиатура с основными командами"""
        keyboard = VkKeyboard(inline=False)

        keyboard.add_button('📍 Поиск рядом', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('🌿 Совет', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('👤 Профиль', color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button('📋 Помощь', color=VkKeyboardColor.SECONDARY)

        return keyboard.get_keyboard()