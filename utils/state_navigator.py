from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State


class StateNavigator:
    @staticmethod
    async def push(
            state: FSMContext,
            new_state: State,
            message_key: str,
            markup_func_name: str | None = None,
            params: dict[str: str] | None = None
    ):
        """
        Добавляет новое состояние в стек истории.
        Также запускает Reminder, если состояние не является начальным или финальным.
        """
        """
        Добавляет новое состояние в стек истории.
        """
        data = await state.get_data()
        history = data.get("history", [])
        history.append({
            "state": new_state.state,
            "message_key": message_key,
            "markup": markup_func_name,
            "params": params
        })
        await state.update_data(history=history)
        await state.set_state(new_state)

    @staticmethod
    async def pop(state: FSMContext) -> dict | None:
        """
        Возвращает предыдущее состояние из стека и переводит пользователя на него.
        Возвращает словарь с ключами: state, message_key, markup.
        """
        data = await state.get_data()
        history = data.get("history", [])
        if len(history) >= 2:
            history.pop()
            previous = history[-1]
            await state.update_data(history=history)
            await state.set_state(previous["state"])

            return previous

        return None
