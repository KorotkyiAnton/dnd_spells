from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from typing import Callable, Dict, Any, Union

from utils.action_log import ActionLogger


class LogMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable,
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]
    ) -> Any:
        state: FSMContext = data.get("state")
        user_id = event.from_user.id

        action = ""
        if isinstance(event, Message):
            action = event.text
        elif isinstance(event, CallbackQuery):
            action = event.data

        try:
            result = await handler(event, data)
            await ActionLogger.log_action(user_id, state, action, result)
            return result
        except Exception as e:
            await ActionLogger.log_action(user_id, state, action, str(e))
            raise
