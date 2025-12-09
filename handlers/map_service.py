from vkbottle.bot import BotLabeler, Message
from database.db import db
from keyboards.key_builders import get_map_filter_kb

bl = BotLabeler()


@bl.message(text="🗺 Карта эко-точек")
async def map_menu(message: Message):
    await message.answer("Что ищем?", keyboard=get_map_filter_kb())


@bl.message(text="♻️ Переработка")
async def show_recycling(message: Message):
    # Получаем точки из БД
    points = await db.queries.get_eco_points(db.conn, category='recycle')

    if not points:
        await message.answer("Точек пока нет в базе.")
        return

    response = "📍 Ближайшие пункты приема:\n\n"
    for p in points:
        response += f"🏢 {p['name']}\nℹ️ {p['description']}\n\n"

    # Здесь можно добавить интеграцию с Яндекс.Картами (Static API) для генерации картинки
    await message.answer(response)


@bl.message(text="📅 Мероприятия")
async def show_events(message: Message):
    points = await db.queries.get_eco_points(db.conn, category='event')
    response = "🌿 Эко-события:\n\n"
    for p in points:
        response += f"🎉 {p['name']}\nℹ️ {p['description']}\n\n"
    await message.answer(response)