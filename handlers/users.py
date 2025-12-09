from vkbottle import Bot, BotBlueprint
from vkbottle.bot import Message


def setup_users(bot: Bot):
    """Регистрирует все обработчики"""

    @bot.on.message(text="привет")
    async def hello_handler(message: Message):
        await message.answer("Привет от бота!")

    @bot.on.message(text="помощь")
    async def help_handler(message: Message):
        await message.answer("Доступные команды: привет, помощь")