import os
import ujson
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any


class MessagesMiddleware(BaseMiddleware):
    def __init__(self, path: str = "../messages/messages.json"):
        self.messages_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)

        with open(self.messages_path, "r", encoding="utf-8") as f:
            self.messages = ujson.load(f)

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Any],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        data["messages"] = self.messages
        return await handler(event, data)
