"""Morphology Item database model."""
from sqlalchemy import Column, Integer, String, Text
from src.database import Base


class MorphologyItem(Base):
    """Model for storing Quranic morphology data."""

    __tablename__ = "morphology_items"

    id = Column(Integer, primary_key=True, index=True)
    chapter = Column(Integer, nullable=False, index=True)
    verse = Column(Integer, nullable=False, index=True)
    word_num = Column(Integer, nullable=False, index=True)
    token = Column(Integer, nullable=False, index=True)
    word = Column(String(255))  # Arabic word (optional)
    tag = Column(String(50), nullable=False)  # Part of speech tag
    info = Column(Text, nullable=False)  # Morphological information

    def __repr__(self):
        return f"<MorphologyItem {self.chapter}:{self.verse}:{self.word_num}:{self.token}>"
