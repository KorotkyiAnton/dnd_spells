from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Spell, CharacterClass


async def search_spells(session: AsyncSession, query: str) -> list[Spell]:
    stmt = (
        select(Spell)
        .where(or_(
            Spell.name_ua.ilike(f"%{query}%"),
            Spell.name_en.ilike(f"%{query}%"),
        ))
        .limit(20)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_spell_by_id(session: AsyncSession, spell_id: int) -> Spell | None:
    stmt = (
        select(Spell)
        .where(Spell.id == spell_id)
        .options(selectinload(Spell.classes))
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
