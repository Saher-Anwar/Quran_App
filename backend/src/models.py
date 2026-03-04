"""Global database models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from src.database import Base


class Surah(Base):
    """Model for storing Surah (Chapter) information."""

    __tablename__ = "surahs"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, unique=True, nullable=False, index=True)
    name_arabic = Column(String(255), nullable=False)  # Arabic name with diacritics
    name_english = Column(String(255), nullable=False)
    revelation_place = Column(String(50))  # Meccan or Medinan
    verses_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Surah {self.number}: {self.name_arabic}>"
