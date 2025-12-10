from vkbottle.bot import BotLabeler, Message

from app.utils import eco_status
from cachemanager import CacheManager

bl = BotLabeler()


@bl.message(config=None, text="👤 Профиль")
async def profile_handler(message: Message, cache: CacheManager):
    user_info = await message.get_user()
    user = cache.get_user(user_info.id)

    if not user:
        await message.answer("Нажмите 'Начать' для регистрации.")
        return

    text = (
        f"👤 Эко-профиль: {user.user_name}\n"
        f"⭐️ Очки кармы: {user.score}\n"
        f"🏅 Звание: {eco_status(user.score)}"
    )
    await message.answer(text)


@bl.message(config=None, text="🏆 Рейтинг")
async def rating_handler(message: Message, cache: CacheManager):
    top_users = cache.get_tops()

    text = "🏆 Топ-10 Эко-активистов:\n"
    for i, u in enumerate(top_users, 1):
        user = cache.get_user(u)
        text += f"{i}. {user.user_name} ({eco_status(user.score)}) — {user.score} очков\n"

    await message.answer(text)