import random

from vkbottle.bot import BotLabeler, Message, Bot, MessageEvent
from vkbottle import GroupEventType, BaseStateGroup, GroupTypes

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
    NAME_STATE = 'write_name'


@bl.message(config=None, text=["Начать", "Start", "Ку"])
async def start_handler(message: Message, bot: Bot, cache: CacheManager):
    user_info = await message.get_user()
    user = cache.get_user(user_info.id)

    text = (
        f"Привет, {user.user_name if user else 'друг'}! Я твой Экологический помощник. 🌿\n"
        "Я помогу тебе найти пункты переработки и стать экологичнее."
    )

    # Регистрация пользователя
    if not user:
        text += '\nДавай знакомится! Как тебя зовут?'

        await bot.state_dispenser.set(message.peer_id, SuperStates.NAME_STATE)
        return text

    await message.answer(text, keyboard=get_main_menu())


@bl.message(config=None, state=SuperStates.NAME_STATE)
async def write_name(message: Message, cache: CacheManager, bot: Bot):
    name = message.text
    user_info = await message.get_user()
    chat_id = message.chat_id

    cache.add_user(User(user_id=user_info.id, user_name=name, user_chats={chat_id}))

    await bot.state_dispenser.delete(message.peer_id)

    await message.answer(f'Тебя зовут {name}?', keyboard=get_name_accept())


@bl.message(config=None, text='Нет')
async def not_accept_name(message: Message, bot: Bot):

    text = 'Извини, не расслышал сразу. Повтори, пожалуйста'
    await bot.state_dispenser.set(message.peer_id, SuperStates.NAME_STATE)
    return text


@bl.message(config=None, text='Да')
async def accept_name(message: Message, cache: CacheManager):
    user_info = await message.get_user()
    user = cache.get_user(user_info.id)

    if not user:
        await message.answer("Нажмите 'Начать' для регистрации.")
        return

    text = (
        f"Привет, {user.user_name}! Я твой Экологический помощник. 🌿\n"
        "Я помогу тебе найти пункты переработки и стать экологичнее."
    )

    await message.answer(text, keyboard=get_main_menu())

@bl.message(config=None, text="🌱 Эко-совет")
async def tip_handler(message: Message, cache: CacheManager):
    user_info = await message.get_user()
    user = cache.get_user(user_info.id)

    if not user:
        await message.answer("Нажмите 'Начать' для регистрации.")
        return

    # Геймификация: начисляем 1 балл за интерес
    if user.today_done.eco_rec == False:
        user.today_done.eco_rec = True
        user.score += 1
        cache.update_tops(user)

    tip = random.choice(ECO_TIPS)
    await message.answer(f"💡 Совет дня:\n\n<b>{tip}</b>", disable_mentions=1)