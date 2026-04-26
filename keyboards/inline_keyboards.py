from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_inline_keyboard(
        *buttons: str,
        callback_data: list = None,
        url_buttons: list = None,
        sizes: tuple = (2,)
):
    """
    Parameters:
    - buttons: текст кнопок
    - callback_data: список callback_data для кнопок, якщо потрібно
    - url_buttons: список URL для кнопок, якщо є URL-кнопки
    - sizes: визначає кількість кнопок у рядку

    Примітка: якщо для кнопки є і URL, і callback_data, пріоритет надається URL.
    """
    keyboard = InlineKeyboardBuilder()

    for index, text in enumerate(buttons):
        if url_buttons and index < len(url_buttons) and url_buttons[index]:
            keyboard.add(InlineKeyboardButton(text=text, url=url_buttons[index]))
        elif callback_data and index < len(callback_data):
            keyboard.add(InlineKeyboardButton(text=text, callback_data=callback_data[index]))
        else:
            keyboard.add(InlineKeyboardButton(text=text, callback_data=f"callback_{index}"))

    return keyboard.adjust(*sizes).as_markup()
