from sqlalchemy import DateTime, String, Text, ForeignKey, Integer, Table, Column, func, quoted_name, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    date_create: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    date_update: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


spell_classes = Table(
    "spell_classes",
    Base.metadata,
    Column("spell_id", ForeignKey("spells.id"), primary_key=True),
    Column("class_id", ForeignKey("classes.id"), primary_key=True),
)


class Spell(Base):
    __tablename__ = "spells"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_ua: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(255))
    level: Mapped[str | None] = mapped_column(String(100))
    casting_time: Mapped[str | None] = mapped_column(String(100))
    duration: Mapped[str | None] = mapped_column(String(100))
    range: Mapped[str | None] = mapped_column(quoted_name("range", True), String(100))
    components: Mapped[str | None] = mapped_column(String(100))
    source: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(String(512))

    classes: Mapped[list["CharacterClass"]] = relationship(
        "CharacterClass", secondary=spell_classes, back_populates="spells", lazy="selectin"
    )


class CharacterClass(Base):
    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    spells: Mapped[list["Spell"]] = relationship(
        "Spell", secondary=spell_classes, back_populates="classes"
    )
