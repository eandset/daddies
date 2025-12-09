from vkbottle.bot import BotLabeler, Message
from database.db import db
from keyboards.key_builders import get_main_menu
import random

bl = BotLabeler()

ECO_TIPS = [
    "Используйте многоразовую бутылку для воды вместо пластиковых.",
    "Выключайте воду, когда чистите зубы. Это экономит до 10 литров в минуту!",
    "Сдавайте батарейки в специальные пункты приема, одна батарейка загрязняет 20 кв.м земли."
]


@bl.message(text=["Начать", "Start", "Ку"])
async def start_handler(message: Message):
    user_info = await message.get_user()

    # Регистрация пользователя через aiosql
    await db.queries.register_user(db.conn, vk_id=message.from_id, first_name=user_info.first_name)
    await db.conn.commit()

    text = (
        f"Привет, {user_info.first_name}! Я твой Экологический помощник. 🌿\n"
        "Я помогу тебе найти пункты переработки и стать экологичнее."
    )
    await message.answer(text, keyboard=get_main_menu())


@bl.message(text="🌱 Эко-совет")
async def tip_handler(message: Message):
    tip = random.choice(ECO_TIPS)
    await message.answer(f"💡 Совет дня:\n{tip}")

    # Геймификация: начисляем 1 балл за интерес
    await db.queries.add_score(db.conn, points=1, vk_id=message.from_id)
    await db.conn.commit()