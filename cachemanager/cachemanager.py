import asyncio
from typing import Dict, Optional, Any

from database import Database
from database import User, Chat
from app.overpass_integration import OverpassIntegration


class CacheManager:
    def __init__(self, database: Database, overpass: OverpassIntegration):
        self.db = database
        self.ov = overpass

        self.users: Dict[int, User] = {}
        self.chats: Dict[int, Chat] = {}
        self.tops: list = []
        self.points: Dict[str, Any] = {}

        self.lock_points: Dict[str, asyncio.Lock] = {}

    def add_user(self, user: User) -> bool:
        self.users[user.user_id] = user
        return True

    def get_user(self, user_id: int) -> Optional[User]:
        if user_id in self.users:
            print(self.users[user_id])
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

        if topers == []:
            return self.tops.append(user.user_id)

        for i, toper in enumerate(topers):
            if self.get_user(toper).score < user.score:
                topers.insert(i, user.user_id)
                break
                
        self.tops = topers[:10]

    def get_tops(self) -> list:
        return self.tops

    async def get_or_create_points(self, location: str):
        if location not in self.points:
            if location not in self.lock_points:
                self.lock_points[location] = asyncio.Lock()

            async with self.lock_points[location]:
                if location not in self.points:
                    parts = location.split('_')
                    lat = parts[0]
                    lon = parts[1]

                    points = await self.ov.find_eco_points(lat, lon)
                    self.points[location] = points
        return self.points[location]

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
        self.chats = await self.db.get_all_chats()
        self.users = await self.db.get_all_users()
        self.tops = await self.db.get_tops()

        return True