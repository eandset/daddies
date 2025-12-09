from typing import Union, Dict, Any

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

    def get_user(self, user_id: int) -> User:
        return self.users[user_id]

    def add_chat(self, chat: Chat) -> bool:
        self.chats[chat.chat_id] = chat
        return True

    def get_chat(self, chat_id: int) -> Chat:
        return self.chats[chat_id]

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
        status = True

