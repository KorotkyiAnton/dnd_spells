from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def _add_spell_buttons(builder: InlineKeyboardBuilder, spells: list) -> None:
    for spell in spells:
        if isinstance(spell, dict):
            spell_id, name_ua, name_en = spell["id"], spell["name_ua"], spell.get("name_en") or ""
        else:
            spell_id, name_ua, name_en = spell.id, spell.name_ua, spell.name_en or ""
        label = f"{name_ua} [{name_en}]" if name_en else name_ua
        builder.button(text=label, callback_data=f"spell:{spell_id}")


def spells_list_kb(spells: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    _add_spell_buttons(builder, spells)
    builder.button(text="🔍 Новий пошук", callback_data="new_search")
    builder.adjust(1)
    return builder.as_markup()


def new_search_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 Новий пошук", callback_data="new_search")
    return builder.as_markup()


def spell_detail_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="↩ До результатів", callback_data="back_to_results")
    builder.button(text="🔍 Новий пошук", callback_data="new_search")
    builder.adjust(1)
    return builder.as_markup()
