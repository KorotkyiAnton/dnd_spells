from aiogram import Router, types

from filters.chat_types import ChatTypeFilter

unknown_router = Router()


# Реагуємо тільки в приватних чатах — у групах мовчимо
@unknown_router.message(ChatTypeFilter(["private"]))
async def unknown_message(message: types.Message, messages: dict):
    await message.answer(messages["unknown_message"])


# Зупиняємо індикатор завантаження на кнопці для будь-якого непрацюючого callback
@unknown_router.callback_query()
async def unknown_callback(callback: types.CallbackQuery):
    await callback.answer()