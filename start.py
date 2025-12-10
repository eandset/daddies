from typing import Optional, Dict, Any

from vkbottle import Bot

from cachemanager import CacheManager
from database import Database


class Classes():
    def __init__(self, db: Database = None, cache: CacheManager = None, bot: Bot = None):
        self.db: Optional[Database] = db
        self.cache: Optional[CacheManager] = cache
        self.bot: Optional[Bot] = bot

    def update_classes(self, db: Database, cache: CacheManager, bot: Bot):
        self.db: Database = db
        self.cache: CacheManager = cache
        self.bot: Bot = bot

    def get_to_dict(self) -> Dict[str, Any]:
        return {'db': self.db, 'cache': self.cache, 'bot': self.bot}
    
    
classes = Classes()