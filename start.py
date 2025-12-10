from typing import Optional, Dict, Any

from vkbottle import Bot

from cachemanager import CacheManager
from database import Database
from app.auto_notifications import AutoNotifivator


class Classes():
    def __init__(self, db: Database = None, cache: CacheManager = None,
                 bot: Bot = None, autonote: AutoNotifivator = None):
        self.db: Optional[Database] = db
        self.cache: Optional[CacheManager] = cache
        self.bot: Optional[Bot] = bot
        self.autonote :Optional[AutoNotifivator] = autonote

    def update_classes(self, db: Database, cache: CacheManager, 
                       bot: Bot, autonote: AutoNotifivator):
        self.db: Database = db
        self.cache: CacheManager = cache
        self.bot: Bot = bot
        self.autonote: AutoNotifivator = autonote

    def get_to_dict(self) -> Dict[str, Any]:
        return {'db': self.db, 'cache': self.cache, 'bot': self.bot, 'autonote': self.autonote}
    
    
classes = Classes()