from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Spell
from database.orm_query import search_spells, get_spell_by_id


async def search_spells_service(session: AsyncSession, query: str) -> list[Spell]:
    return await search_spells(session, query)


async def get_spell_service(session: AsyncSession, spell_id: int) -> Spell | None:
    return await get_spell_by_id(session, spell_id)
