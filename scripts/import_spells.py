import json
import os
from sqlalchemy import text
from database.engine import session_maker


def _clip(val, max_len):
    return (val or "")[:max_len]


async def import_spells_if_empty():
    async with session_maker() as session:
        print("[import] Очищення таблиць...")
        await session.execute(text(
            "TRUNCATE TABLE spell_classes, spells, classes RESTART IDENTITY CASCADE"
        ))

        print("[import] Починаємо імпорт...")

        json_path = os.path.join(os.path.dirname(__file__), "../spells_ua.json")
        with open(json_path, encoding="utf-8") as f:
            spells = json.load(f)

        for spell in spells:
            result = await session.execute(text("""
                INSERT INTO spells (name_ua, name_en, level, casting_time, duration, "range", components, source, description, url)
                VALUES (:name_ua, :name_en, :level, :casting_time, :duration, :range, :components, :source, :description, :url)
                RETURNING id
            """), {
                "name_ua":      _clip(spell.get("name_ua"), 255),
                "name_en":      _clip(spell.get("name_en"), 255),
                "level":        _clip(spell.get("level"), 100),
                "casting_time": _clip(spell.get("casting_time"), 100),
                "duration":     _clip(spell.get("duration"), 100),
                "range":        _clip(spell.get("range"), 100),
                "components":   _clip(spell.get("components"), 100),
                "source":       _clip(spell.get("source"), 255),
                "description":  spell.get("description") or "",
                "url":          _clip(spell.get("url"), 512),
            })
            spell_id = result.scalar()

            class_names = [c.strip() for c in spell.get("classes", "").split(",") if c.strip()]
            for class_name in class_names:
                cls_result = await session.execute(text("""
                    INSERT INTO classes (name) VALUES (:name)
                    ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                    RETURNING id
                """), {"name": class_name})
                class_id = cls_result.scalar()

                await session.execute(text("""
                    INSERT INTO spell_classes (spell_id, class_id) VALUES (:spell_id, :class_id)
                    ON CONFLICT DO NOTHING
                """), {"spell_id": spell_id, "class_id": class_id})

        await session.commit()
        print(f"[import] Імпортовано {len(spells)} заклять")
