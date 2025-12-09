from vkbottle.bot import BotLabeler, Message
from database.db import db

bl = BotLabeler()


@bl.message(text="👤 Профиль")
async def profile_handler(message: Message):
    user = await db.queries.get_user(db.conn, vk_id=message.from_id)

    if not user:
        await message.answer("Нажмите 'Начать' для регистрации.")
        return

    text = (
        f"👤 Эко-профиль: {user['first_name']}\n"
        f"⭐️ Очки кармы: {user['eco_points']}\n"
        f"🏅 Звание: {user['eco_level']}"
    )
    await message.answer(text)


@bl.message(text="🏆 Рейтинг")
async def rating_handler(message: Message):
    top_users = await db.queries.get_top_users(db.conn)

    text = "🏆 Топ-10 Эко-активистов:\n"
    for i, u in enumerate(top_users, 1):
        text += f"{i}. {u['first_name']} — {u['eco_points']} очков\n"

    await message.answer(text)