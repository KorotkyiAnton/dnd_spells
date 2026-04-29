import json
import os
from sqlalchemy import text
from database.engine import session_maker

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
                "name_ua":      spell.get("name_ua", ""),
                "name_en":      spell.get("name_en", ""),
                "level":        spell.get("level", ""),
                "casting_time": spell.get("casting_time", ""),
                "duration":     spell.get("duration", ""),
                "range":        spell.get("range", ""),
                "components":   spell.get("components", ""),
                "source":       spell.get("source", ""),
                "description":  spell.get("description", ""),
                "url":          spell.get("url", ""),
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
