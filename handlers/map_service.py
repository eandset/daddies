from vkbottle.bot import BotLabeler, Message, MessageEvent
from vkbottle import GroupEventType

from keyboards.key_builders import get_map_filter_kb, write_location
from cachemanager import CacheManager
from rules import PayloadRule

bl = BotLabeler()


@bl.message(text="🗺 Карта эко-точек")
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


@bl.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule('command', 'write_lovation'))
async def write_location(event: MessageEvent, cache: CacheManager):
    user_info = event.user_id
    user = cache.get_user(user_info.id)

    location = None # Определите локу

    user.location = location

    await event.edit_message("Что ищем?", keyboard=get_map_filter_kb())

@bl.message(text="♻️ Переработка")
async def show_recycling(message: Message, cache: CacheManager):
    user_info = await message.get_user()
    user = cache.get_user(user_info.id)

    if not user or not user.location:
        await message.answer("Нажмите 'Начать' для регистрации.")
        return

    points = await cache.get_or_create_points(user.location)
    points = points['recycling']

    if not points:
        await message.answer("Точек пока нет в базе.")
        return

    response = "📍 Ближайшие пункты приема:\n\n"
    for p in points:
        response += f"🏢 {p['name']}\nℹ️ {p['description']}\n\n"

    # Здесь можно добавить интеграцию с Яндекс.Картами (Static API) для генерации картинки
    await message.answer(response)


@bl.message(text="📅 Мероприятия")
async def show_events(message: Message, cache: CacheManager):
    user_info = await message.get_user()
    user = cache.get_user(user_info.id)

    if not user or not user.location:
        await message.answer("Нажмите 'Начать' для регистрации.")
        return

    points = await cache.get_or_create_points(user.location)
    points = points['event']

    if not points:
        await message.answer("Точек пока нет в базе.")
        return
    
    response = "🌿 Эко-события:\n\n"
    for p in points:
        response += f"🎉 {p['name']}\nℹ️ {p['description']}\n\n"
    await message.answer(response)