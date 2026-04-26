import html

from database.models import Spell


def format_spell_card(spell: Spell, template: str) -> str:
    def esc(val: str | None) -> str:
        return html.escape(val or "—")

    classes_str = ", ".join(c.name for c in (spell.classes or []))
    name_en = html.escape(spell.name_en or "")

    return template.format(
        name_ua=html.escape(spell.name_ua or ""),
        name_en_part=f" [{name_en}]" if name_en else "",
        level=esc(spell.level),
        casting_time=esc(spell.casting_time),
        duration=esc(spell.duration),
        spell_range=esc(spell.range),
        components=esc(spell.components),
        classes=html.escape(classes_str) if classes_str else "—",
        source=esc(spell.source),
        description=esc(spell.description),
    )