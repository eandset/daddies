from vkbottle.bot import BotLabeler, Message, MessageEvent
from vkbottle import GroupEventType

from keyboards.key_builders import get_map_filter_kb, write_location
from cachemanager import CacheManager
from rules import PayloadRule

bl = BotLabeler()


@bl.message(config=None, text="🗺 Карта эко-точек")
async def map_menu(message: Message, cache: CacheManager):
    user_info = await message.get_user()
    user = cache.get_user(user_info.id)

    if not user:
        await message.answer("Нажмите 'Начать' для регистрации.")
        return

    if user.location:
        await message.answer("Что ищем?", keyboard=get_map_filter_kb())
    else:
        await message.answer('Необходимо обновить местоположение', keyboard=write_location())


@bl.message(config=None, text='Обновить')
async def write_loc(message: Message, cache: CacheManager):
    user_info = await message.get_user()
    user = cache.get_user(user_info.id)

    if not user:
        await message.answer("Нажмите 'Начать' для регистрации.")
        return

    location = "40, 50"  # Заглушка, нужно реализовать получение местоположения
    user.location = location
    cache.add_user(user)  # Важно обновить пользователя в кэше
    
    await message.answer("Что ищем?", keyboard=get_map_filter_kb())


@bl.message(config=None, text="♻️ Переработка")
async def show_recycling(message: Message, cache: CacheManager):
    user_info = await message.get_user()
    user = cache.get_user(user_info.id)

    if not user or not user.location:
        await message.answer("Нажмите 'Начать' для регистрации.")
        return

    try:
        
        # Здесь можно добавить интеграцию с Яндекс.Картами (Static API) для генерации картинки
        await message.answer("ЗАГЛУШКА #$@#$")
        
    except Exception as e:
        await message.answer(f"Произошла ошибка при получении точек: {str(e)}")


@bl.message(config=None, text="📅 Мероприятия")
async def show_events(message: Message, cache: CacheManager):
    user_info = await message.get_user()
    user = cache.get_user(user_info.id)

    if not user or not user.location:
        await message.answer("Нажмите 'Начать' для регистрации.")
        return

    try:
        points_data = await cache.get_or_create_points(user.location)
        
        # Проверяем структуру данных
        if 'points' in points_data:
            points = points_data['points']
        elif 'event' in points_data or 'events' in points_data:
            points = points_data.get('event') or points_data.get('events', [])
        else:
            points = points_data
            
        if not points or (isinstance(points, dict) and 'points' in points and not points['points']):
            await message.answer("Эко-событий пока нет в базе.")
            return

        response = "🌿 Эко-события:\n\n"
        
        # Обрабатываем разные форматы точек
        if isinstance(points, dict) and 'points' in points:
            points_list = points['points']
        elif isinstance(points, list):
            points_list = points
        else:
            points_list = [points]
        
        for p in points_list[:10]:  # Ограничиваем вывод 10 событиями
            if isinstance(p, dict):
                name = p.get('name', 'Неизвестное событие')
                description = p.get('description', 'Описание отсутствует')
                date = p.get('date', 'Дата не указана')
                time = p.get('time', '')
                
                response += f"🎉 {name}\n"
                if date:
                    response += f"📅 {date}"
                    if time:
                        response += f" в {time}"
                    response += "\n"
                response += f"ℹ️ {description}\n\n"
            else:
                response += f"🎉 {str(p)}\n\n"
                
        await message.answer(response)
        
    except Exception as e:
        await message.answer(f"Произошла ошибка при получении событий: {str(e)}")