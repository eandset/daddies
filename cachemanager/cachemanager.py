import asyncio
from typing import Dict, Optional, Any, List
import json

from database.database import Database
from database.models import User, Chat


class CacheManager:
    def __init__(self, database: Database):
        self.db = database

        self.users: Dict[int, User] = {}
        self.chats: Dict[int, Chat] = {}
        self.tops: List[int] = []
        self.points: Dict[str, Any] = {}

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

        if not topers:  # Более питонический способ проверки пустого списка
            self.tops.append(user.user_id)
            return True

        # Проверяем, что пользователь существует в кэше
        if not self.get_user(user.user_id):
            self.users[user.user_id] = user

        # Проверяем, есть ли пользователь уже в топе
        if user.user_id in topers:
            topers.remove(user.user_id)

        inserted = False
        for i, toper in enumerate(topers):
            toper_user = self.get_user(toper)
            if toper_user and user.score > toper_user.score:
                topers.insert(i, user.user_id)
                inserted = True
                break
        
        if not inserted:
            topers.append(user.user_id)
                
        self.tops = topers[:10]
        return True

    def get_tops(self) -> List[int]:
        return self.tops

    async def save_data_to_db(self) -> bool:
        status = True

        for user in self.users.values():
            if not await self.db.save_user(user):
                status = False

        for chat in self.chats.values():
            if not await self.db.save_chat(chat):
                status = False

        if not await self.db.save_tops(self.tops):
            status = False

        return status

    async def get_data_from_db(self) -> bool:
        try:
            self.chats = await self.db.get_all_chats()
            self.users = await self.db.get_all_users()
            self.tops = await self.db.get_tops()
            return True
        except Exception as e:
            print(f"Error loading data from DB: {e}")
            return False