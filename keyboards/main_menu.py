from vk_api.keyboard import VkKeyboard, VkKeyboardColor


class MainMenuKeyboard:
    def __init__(self):
        self.keyboard = VkKeyboard(one_time=False)

        # Первый ряд
        self.keyboard.add_button('🗺️ Пункты приёма', color=VkKeyboardColor.PRIMARY)
        self.keyboard.add_button('📅 События', color=VkKeyboardColor.PRIMARY)

        # Второй ряд
        self.keyboard.add_line()
        self.keyboard.add_button('🌿 Советы', color=VkKeyboardColor.SECONDARY)
        self.keyboard.add_button('🏆 Рейтинг', color=VkKeyboardColor.SECONDARY)

        # Третий ряд
        self.keyboard.add_line()
        self.keyboard.add_button('👤 Профиль', color=VkKeyboardColor.SECONDARY)
        self.keyboard.add_button('💬 Отзыв', color=VkKeyboardColor.SECONDARY)

        # Четвертый ряд
        self.keyboard.add_line()
        self.keyboard.add_button('⚙️ Настройки', color=VkKeyboardColor.SECONDARY)
        self.keyboard.add_button('📋 Помощь', color=VkKeyboardColor.SECONDARY)

    def get_keyboard(self):
        return self.keyboard.get_keyboard()