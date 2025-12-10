from vkbottle import Keyboard, KeyboardButtonColor, Text

def get_main_menu():
    keyboard = Keyboard(one_time=False, inline=False)
    keyboard.add(Text("🌱 Эко-совет",), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("🗺 Карта эко-точек"), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text("👤 Профиль"), color=KeyboardButtonColor.SECONDARY)
    keyboard.add(Text('⚙️ Настройки'), color=KeyboardButtonColor.SECONDARY)
    keyboard.row()
    keyboard.add(Text("🏆 Рейтинг"), color=KeyboardButtonColor.POSITIVE)
    return keyboard.get_json()

def get_map_filter_kb():
    keyboard = Keyboard(inline=True)
    keyboard.add(Text("♻️ Переработка"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("📅 Мероприятия"), color=KeyboardButtonColor.POSITIVE)
    return keyboard.get_json()

def get_name_accept():
    keyboard = Keyboard(inline=True)
    keyboard.add(Text('Да'), color=KeyboardButtonColor.POSITIVE)
    keyboard.add(Text('Нет'), color=KeyboardButtonColor.NEGATIVE)
    return keyboard.get_json()

def write_location():
    keyboard = Keyboard(inline=True)
    keyboard.add(Text('Обновить'), color=KeyboardButtonColor.POSITIVE)
    return keyboard.get_json()

def settings_kb(notification):
    keyboard = Keyboard(inline=True)
    keyboard.add(Text('Псевдоним', payload={'command': 'change_name'}), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text('Местоположение', payload={'command': 'location'}), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    text = f'Уведомления: {"Вкл." if notification else "Выкл."}'
    keyboard.add(Text(text, payload={'command': 'notification'}), color=KeyboardButtonColor.SECONDARY)
    keyboard.row()
    keyboard.add(Text('Тест', payload={'command': 'update'}), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()