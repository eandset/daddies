import asyncio
from typing import Dict, Optional, Any

from database.database import Database
from database.models import User, Chat


class CacheManager:
    def __init__(self, database: Database):
        self.db = database

        self.users: Dict[int, User] = {}
        self.chats: Dict[int, Chat] = {}
        self.tops: list = []
        self.points: Dict[str, Any]

        self.lock_points: Dict[str, asyncio.Lock] = {}

    def add_user(self, user: User) -> bool:
        self.users[user.user_id] = user
        return True

    def get_user(self, user_id: int) -> Optional[User]:
        if user_id in self.users:
            return self.users[user_id]
        return None

    def add_chat(self, chat: Chat) -> bool:
        self.chats[chat.chat_id] = chat
        return True

    def get_chat(self, chat_id: int) -> Optional[Chat]:
        if chat_id in self.chats:
            return self.chats[chat_id]
        return None
    
    def update_tops(self, user: User) -> bool:
        topers = self.tops
        for i, toper in enumerate(topers):
            if self.get_user(toper).score < user.score:
                topers.insert(i, user.user_id)
                break
        
        self.tops = toper[:10]

    def get_tops(self) -> list:
        return self.tops

    async def get_or_create_points(self, location: str):
        if location not in self.points:
            if location not in self.lock_points:
                self.lock_points[location] = asyncio.Lock()

            async with self.lock_points[location]:
                if location not in self.points:
                    pass # Вот тут добавить как мы определяем точки

        return self.points[location]

    async def save_data_to_db(self) -> bool:
        status = True

        for k, user in self.users.keys():
            if not await self.db.save_user(user):
                status = False

        for k, chat in self.chats.keys():
            if not await self.db.save_chat(chat):
                status = False

        if not self.db.save_tops(self.tops):
            status = False

        return status

    async def get_data_from_db(self) -> bool:
        self.chats = await self.db.get_all_chats()
        self.users = await self.db.get_all_users()
        self.tops = await self.db.get_tops()

        return True