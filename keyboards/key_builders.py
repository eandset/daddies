from vkbottle import Keyboard, KeyboardButtonColor, Text

def get_main_menu():
    keyboard = Keyboard(one_time=False, inline=False)
    keyboard.add(Text("🗺 Карта эко-точек"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("👤 Профиль"), color=KeyboardButtonColor.POSITIVE)
    keyboard.row()
    keyboard.add(Text("🌱 Эко-совет",), color=KeyboardButtonColor.SECONDARY)
    keyboard.add(Text("🏆 Рейтинг"), color=KeyboardButtonColor.SECONDARY)
    return keyboard

def get_map_filter_kb():
    keyboard = Keyboard(inline=True)
    keyboard.add(Text("♻️ Переработка"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("📅 Мероприятия"), color=KeyboardButtonColor.POSITIVE)
    return keyboard

def get_name_accept():
    keyboard = Keyboard(inline=True)
    keyboard.add(Text('Да', payload={'command': 'accept_name'}), color=KeyboardButtonColor.POSITIVE)
    keyboard.add(Text('Нет', payload={'command': 'not_accept_name'}), color=KeyboardButtonColor.NEGATIVE)
    return keyboard

def write_location():
    keyboard = Keyboard(inline=True)
    keyboard.add(Text('Обновить', payload={'command': 'update_location'}), color=KeyboardButtonColor.POSITIVE)
    return keyboard