from vkbottle.dispatch.rules.base import ABCRule
from vkbottle.bot import MessageEvent

class PayloadRule(ABCRule[MessageEvent]):
    def __init__(self, payload_key: str, payload_value: str):
        # Правило будет срабатывать, когда payload содержит нужную пару ключ-значение
        self.payload_key = payload_key
        self.payload_value = payload_value

    async def check(self, event: MessageEvent) -> bool:
        # Проверяем, совпадает ли значение по указанному ключу
        return event.payload.get(self.payload_key) == self.payload_value
    
    