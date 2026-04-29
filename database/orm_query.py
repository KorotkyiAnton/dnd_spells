import re
from sqlalchemy import select, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Spell


def _pg_escape(s: str) -> str:
    return re.sub(r'([\\.+*?\[\]^$(){}=!<>|:\-#~])', r'\\\1', s)


async def search_spells(session: AsyncSession, query: str) -> list[Spell]:
    q = query.strip()
    partial = f"%{q}%"
    word_re = f"\\y{_pg_escape(q)}\\y"

    priority = case(
        (Spell.name_ua.ilike(q), 1),
        (Spell.name_en.ilike(q), 2),
        (Spell.name_ua.ilike(partial), 3),
        (Spell.name_en.ilike(partial), 4),
        (Spell.description.op("~*")(word_re), 5),
        (Spell.description.ilike(partial), 6),
        else_=99,
    )

    stmt = (
        select(Spell)
        .where(or_(
            Spell.name_ua.ilike(q),
            Spell.name_en.ilike(q),
            Spell.name_ua.ilike(partial),
            Spell.name_en.ilike(partial),
            Spell.description.op("~*")(word_re),
            Spell.description.ilike(partial),
        ))
        .order_by(priority)
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