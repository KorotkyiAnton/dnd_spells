import json
import os
from sqlalchemy import text
from database.engine import session_maker

async def import_spells_if_empty():
    async with session_maker() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM spells"))
        count = result.scalar()

        if count > 0:
            print(f"[import] БД вже містить {count} заклять, пропускаємо імпорт")
            return

        print("[import] БД порожня, починаємо імпорт...")

        json_path = os.path.join(os.path.dirname(__file__), "../data/spells_ua.json")
        with open(json_path, encoding="utf-8") as f:
            spells = json.load(f)

        for spell in spells:
            await session.execute(text("""
                INSERT INTO spells (name_ua, name_en, level, casting_time, duration, "range", components, source, description, url)
                VALUES (:name_ua, :name_en, :level, :casting_time, :duration, :range, :components, :source, :description, :url)
                ON CONFLICT DO NOTHING
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

        await session.commit()
        print(f"[import] Імпортовано {len(spells)} заклять")
