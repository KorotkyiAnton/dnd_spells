import html
import logging

from aiogram import Bot, types, Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_types import ChatTypeFilter
from keyboards.spell_kb import spells_list_kb, spell_detail_kb, new_search_kb
from services.spell_formatter import format_spell_card
from services.spell_service import get_spell_service, search_spells_service

logger = logging.getLogger(__name__)

common_router = Router()

private_router = Router()
private_router.message.filter(ChatTypeFilter(["private"]))

group_router = Router()
group_router.message.filter(ChatTypeFilter(["group", "supergroup"]))


class SpellStates(StatesGroup):
    has_results = State()


async def _cleanup_prev_result(bot: Bot, chat_id: int, state: FSMContext) -> None:
    """
    detail → убрать все кнопки (оставить текст карточки)
    list   → удалить сообщение
    """
    data = await state.get_data()
    msg_id = data.get("last_result_msg_id")
    msg_type = data.get("last_result_type")
    if not msg_id:
        return
    try:
        if msg_type == "detail":
            await bot.edit_message_reply_markup(
                chat_id=chat_id, message_id=msg_id, reply_markup=None
            )
        else:
            await bot.delete_message(chat_id, msg_id)
    except TelegramBadRequest:
        logger.info("Could not clean up previous result message %s in chat %s", msg_id, chat_id)


# ── Private: /start | /menu ──────────────────────────────────────────────────

@private_router.message(CommandStart())
@private_router.message(Command("menu"))
async def start_command(message: types.Message, state: FSMContext, messages: dict):
    await state.clear()
    await message.answer(messages["start"])


# ── Private: free-text search ────────────────────────────────────────────────

@private_router.message(F.text & ~F.text.startswith("/"))
async def handle_text_search(message: types.Message, state: FSMContext,
                             session: AsyncSession, messages: dict):
    query = message.text.strip()
    spells = await search_spells_service(session, query)

    if not spells:
        await message.answer(messages["no_results"].format(query=html.escape(query)))
        return

    await _cleanup_prev_result(message.bot, message.chat.id, state)

    if len(spells) == 1:
        spell = await get_spell_service(session, spells[0].id)
        await state.clear()
        sent = await message.answer(format_spell_card(spell, messages["spell_card"]),
                                    reply_markup=new_search_kb())
        await state.update_data(last_result_msg_id=sent.message_id, last_result_type="detail")
        return

    spells_data = [{"id": s.id, "name_ua": s.name_ua, "name_en": s.name_en} for s in spells]
    results_text = messages["results_header"].format(count=len(spells))
    sent = await message.answer(results_text, reply_markup=spells_list_kb(spells_data))
    await state.set_state(SpellStates.has_results)
    await state.update_data(spells=spells_data, results_text=results_text,
                            last_result_msg_id=sent.message_id, last_result_type="list")


# ── Group: /spell <name> ─────────────────────────────────────────────────────

@group_router.message(Command("spell"))
async def handle_group_spell(message: types.Message, state: FSMContext,
                             session: AsyncSession, messages: dict):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.reply(messages["group_usage"])
        return

    query = parts[1].strip()
    spells = await search_spells_service(session, query)

    if not spells:
        await message.reply(messages["no_results"].format(query=html.escape(query)))
        return

    await _cleanup_prev_result(message.bot, message.chat.id, state)

    if len(spells) == 1:
        spell = await get_spell_service(session, spells[0].id)
        await state.clear()
        sent = await message.reply(format_spell_card(spell, messages["spell_card"]),
                                   reply_markup=new_search_kb())
        await state.update_data(last_result_msg_id=sent.message_id, last_result_type="detail")
        return

    spells_data = [{"id": s.id, "name_ua": s.name_ua, "name_en": s.name_en} for s in spells]
    results_text = messages["results_header"].format(count=len(spells))
    sent = await message.reply(results_text, reply_markup=spells_list_kb(spells_data))
    await state.set_state(SpellStates.has_results)
    await state.update_data(spells=spells_data, results_text=results_text,
                            last_result_msg_id=sent.message_id, last_result_type="list")


# ── Callback: spell detail (all chat types) ───────────────────────────────────

@common_router.callback_query(F.data.startswith("spell:"))
async def handle_spell_detail(callback: types.CallbackQuery, state: FSMContext,
                              session: AsyncSession, messages: dict):
    spell_id = int(callback.data.split(":")[1])
    spell = await get_spell_service(session, spell_id)

    if not spell:
        await callback.answer(messages["spell_not_found"], show_alert=True)
        return

    state_data = await state.get_data()
    spells_data = state_data.get("spells", [])

    text = format_spell_card(spell, messages["spell_card"])
    kb = spell_detail_kb() if spells_data else None

    try:
        await callback.message.edit_text(text, reply_markup=kb)
        await state.update_data(last_result_type="detail")
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e).lower():
            sent = await callback.message.answer(text, reply_markup=kb)
            await state.update_data(last_result_msg_id=sent.message_id, last_result_type="detail")

    await callback.answer()


# ── Callback: back to results ─────────────────────────────────────────────────

@common_router.callback_query(F.data == "back_to_results")
async def handle_back_to_results(callback: types.CallbackQuery, state: FSMContext,
                                 messages: dict):
    state_data = await state.get_data()
    spells_data = state_data.get("spells", [])
    results_text = state_data.get("results_text", messages["search_prompt"])

    try:
        await callback.message.edit_text(results_text, reply_markup=spells_list_kb(spells_data))
        await state.update_data(last_result_type="list")
    except TelegramBadRequest:
        sent = await callback.message.answer(results_text, reply_markup=spells_list_kb(spells_data))
        await state.update_data(last_result_msg_id=sent.message_id, last_result_type="list")

    await callback.answer()


# ── Callback: new search ──────────────────────────────────────────────────────

@common_router.callback_query(F.data == "new_search")
async def handle_new_search(callback: types.CallbackQuery, state: FSMContext, messages: dict):
    await _cleanup_prev_result(callback.bot, callback.message.chat.id, state)

    if callback.message.chat.type == "private":
        await state.clear()
        await callback.message.answer(messages["search_prompt"])
        await callback.answer()
    else:
        await callback.answer(messages["group_usage"], show_alert=True)


common_router.include_routers(private_router, group_router)