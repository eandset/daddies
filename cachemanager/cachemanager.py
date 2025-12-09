from typing import Dict, Optional

from database.database import Database
from database.models import User, Chat


class CacheManager:
    def __init__(self, database: Database):
        self.db = database

        self.users: Dict[int, User] = {}
        self.chats: Dict[int, Chat] = {}

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

    async def save_data_to_db(self) -> bool:
        status = True

        for k, user in self.users.keys():
            if not await self.db.save_user(user):
                status = False

        for k, chat in self.chats.keys():
            if not await self.db.save_chat(chat):
                status = False

        return status

    async def get_data_from_db(self) -> bool:
        self.chats = await self.db.get_all_chats()
        self.users = await self.db.get_all_users()

        return True
