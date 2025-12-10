import asyncio
import random

from vkbottle import Bot
from vkbottle.exception_factory import VKAPIError

from cachemanager import CacheManager
from database import User

class AutoNotifivator():
    def __init__(self, bot: Bot, cache_manager: CacheManager):
        self.cache = cache_manager
        self.bot = bot
        self.errors = [901, 902, 7, 15]
        self.is_running = False
        self.task_notification = None

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.task_notification = asyncio.create_task(self.auto_note())
            print('Парсинг запущен')

    async def stop(self):
        self.is_running = False
        if self.task_notification:
            self.task_notification.cancel()
            print('Парсинг остановлен')
            try:
                await self.task_notification
            except asyncio.CancelledError:
                pass

    async def auto_note(self):
            while self.is_running:
                for user in self.cache.users.values():
                    user.today_done.validate()
                    user.preferences.validate()

                    if user.notification:
                        note = self.get_recomendates(user)
                        print('Нотификатим')
                        for user_chat in user.user_chats:
                            try:
                                message = random.choice(note)
                                await self.bot.api.messages.send(
                                    chat_id=user_chat,     
                                    message=message,     
                                    random_id=0
                                )
                            except VKAPIError as e:
                                if e.code in self.errors:
                                    user.notification = False
                                    break

                await asyncio.sleep(60 * 60 * random.randint(12, 32))

    def get_recomendates(self, user: User):
        pref = user.preferences.to_dict()

        actives = list(pref.keys())
        numbers = list(pref.values())

        total = sum(numbers)
        if total <= 0:
            chosen = random.choice(actives)
        else:
            chosen = random.choices(actives, weights=numbers, k=1)[0]
        
        return note[chosen]


note = {
    'recycling': ['А вы знали, что значительная часть мирового океана загрезняна мусором?',
                    'Один фантик на земле не приведёт к катострофе, говорят миллионы людей!'],
    'events': ['Помогая природе, вы помогаете и себе!',
                'Чем больше людей будет заботиться о планете, тем дольше она будет жить.'],
    'shop': ['Здоровая пища продлевает жизнь!',
                'Химия никогда не будет лучше натуральных продуктов'],
    'eco_rec': ['Стремление к знанию — залог успеха!',
                'А вы знали, что помогаете помогаете природе даже своим присутствием здесь']
}