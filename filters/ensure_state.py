from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import get_user_role_by_telegram_id
from handlers.common import PlayerForm, start_command


class EnsureStateMiddleware(BaseMiddleware):
    def __init__(self, default_state: State = PlayerForm.welcome_msg):
        self.default_state = default_state

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        state: FSMContext = data["state"]
        session: AsyncSession = data["session"]
        current_state = await state.get_state()
        messages = data.get("messages", {})
        role = await get_user_role_by_telegram_id(session, event.from_user.id)

        if current_state is None and role in ["player", None]:
            return await start_command(event, state, session, messages, data["user"])

        return await handler(event, data)
