import random

from vkbottle.bot import BotLabeler, Message, Bot, MessageEvent
from vkbottle import GroupEventType, BaseStateGroup

from database import Database, User
from cachemanager import CacheManager
from keyboards.key_builders import get_main_menu, get_name_accept
from rules import PayloadRule


bl = BotLabeler()

ECO_TIPS = [
    "Используйте многоразовую бутылку для воды вместо пластиковых.",
    "Выключайте воду, когда чистите зубы. Это экономит до 10 литров в минуту!",
    "Сдавайте батарейки в специальные пункты приема, одна батарейка загрязняет 20 кв.м земли."
]

class SuperStates(BaseStateGroup):
    NAME_STATE = "write_name"


@bl.message(text=["Начать", "Start", "Ку"])
async def start_handler(message: Message, cache: CacheManager, bot: Bot):
    user_info = await message.get_user()
    text = (
        f"Привет, друг! Я твой Экологический помощник. 🌿\n"
        "Я помогу тебе найти пункты переработки и стать экологичнее."
    )

    # Регистрация пользователя
    user = cache.get_user(user_info.id)
    if not user:
        text += '\nДавай знакомится! Как тебя зовут?'

        await bot.state_dispenser.set(message.peer_id, 'write_name')
        return await message.answer(text)

    await message.answer(text, keyboard=get_main_menu())


@bl.message(state=SuperStates.NAME_STATE)
async def write_name(message: Message, cache: CacheManager):
    name = message.text
    user_info = await message.get_user()
    chat_id = message.chat_id

    cache.add_user(User(user_info.id, name, set(chat_id)))
    await message.answer(f'Тебя зовут <b>{name}</b>?', keyboard=get_name_accept())


@bl.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule('command', 'not_accept_name'))
async def not_accept_name(event: MessageEvent, bot: Bot):
    text = 'Извини, не расслышал сразу. Повтори, пожалуйста'
    await bot.state_dispenser.set(event.peer_id, SuperStates.NAME_STATE)
    return await event.edit_message(text)


@bl.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule('command', 'accept_name'))
async def accept_name(event: MessageEvent, cache: CacheManager):
    user = cache.get_user(event.user_id)
    text = (
        f"Привет, {user.user_name}! Я твой Экологический помощник. 🌿\n"
        "Я помогу тебе найти пункты переработки и стать экологичнее."
    )

    await event.edit_message(text, keyboard=get_main_menu())

@bl.message(text="🌱 Эко-совет")
async def tip_handler(message: Message, cache: CacheManager):
    user_info = await message.get_user()
    user = cache.get_user(user_info.id)

    # Геймификация: начисляем 1 балл за интерес
    if user.today_done.eco_rec == False:
        user.today_done.eco_rec = True
        user.score += 1
        cache.update_tops(user)

    tip = random.choice(ECO_TIPS)
    await message.answer(f"💡 Совет дня:\n\n<b>{tip}</b>")