"""Verse database model."""
from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime
from src.database import Base


class Verse(Base):
    """Model for storing Quranic verses."""

    __tablename__ = "verses"

    id = Column(Integer, primary_key=True, index=True)
    surah_number = Column(Integer, nullable=False, index=True)
    verse_number = Column(Integer, nullable=False, index=True)
    text_arabic = Column(Text, nullable=False)  # Arabic text with diacritics (Uthmani script)
    text_simple = Column(Text)  # Simplified Arabic text without diacritics
    translation_english = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Verse {self.surah_number}:{self.verse_number}>"
