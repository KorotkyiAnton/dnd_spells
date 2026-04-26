"""
Run once to populate the DB from spells_ua.json.
  python scripts/import_spells.py
Idempotent: skips spells already present (matched by name_en + name_ua).
"""
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.models import Base, Spell, CharacterClass, spell_classes

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


async def get_or_create_class(session: AsyncSession, name: str) -> CharacterClass:
    result = await session.execute(select(CharacterClass).where(CharacterClass.name == name))
    obj = result.scalar_one_or_none()
    if obj is None:
        obj = CharacterClass(name=name)
        session.add(obj)
        await session.flush()
    return obj


async def spell_exists(session: AsyncSession, name_ua: str, name_en: str | None) -> bool:
    stmt = select(Spell.id).where(Spell.name_ua == name_ua)
    if name_en:
        stmt = stmt.where(Spell.name_en == name_en)
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None


async def import_spells(data_path: Path, session_maker_: async_sessionmaker) -> None:
    with open(data_path, encoding="utf-8") as f:
        records = json.load(f)

    log.info("Loaded %d records from %s", len(records), data_path)
    inserted = skipped = 0

    async with session_maker_() as session:
        async with session.begin():
            for rec in records:
                name_ua = (rec.get("name_ua") or "").strip()
                name_en = (rec.get("name_en") or "").strip() or None

                if not name_ua:
                    skipped += 1
                    continue

                if await spell_exists(session, name_ua, name_en):
                    skipped += 1
                    continue

                spell = Spell(
                    name_ua=name_ua,
                    name_en=name_en,
                    level=(rec.get("level") or "").strip() or None,
                    casting_time=(rec.get("casting_time") or "").strip() or None,
                    duration=(rec.get("duration") or "").strip() or None,
                    range=(rec.get("range") or "").strip() or None,
                    components=(rec.get("components") or "").strip() or None,
                    source=(rec.get("source") or "").strip() or None,
                    description=(rec.get("description") or "").strip() or None,
                    url=(rec.get("url") or "").strip() or None,
                )
                session.add(spell)
                await session.flush()

                raw_classes = rec.get("classes") or ""
                for cls_name in raw_classes.split(","):
                    cls_name = cls_name.strip()
                    if not cls_name:
                        continue
                    char_class = await get_or_create_class(session, cls_name)
                    await session.execute(
                        spell_classes.insert().values(spell_id=spell.id, class_id=char_class.id)
                    )

                inserted += 1

    log.info("Done — inserted: %d, skipped: %d", inserted, skipped)


async def main() -> None:
    engine = create_async_engine(os.getenv("DATABASE_URL"), echo=False)
    maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    data_path = PROJECT_ROOT / "spells_ua.json"
    await import_spells(data_path, maker)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())