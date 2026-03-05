"""Ism (Word) database model."""
from sqlalchemy import Column, Integer, String, Enum
import enum
from src.database import Base


class HeavinessEnum(enum.Enum):
    """Enum for ism heaviness."""
    LIGHT = "light"
    HEAVY = "heavy"


class IsmTypeEnum(enum.Enum):
    """Enum for ism type."""
    PROPER = "proper"
    COMMON = "common"


class FlexibilityEnum(enum.Enum):
    """Enum for ism flexibility."""
    FLEXIBLE = "flexible"
    PARTIAL = "partial"
    NON_FLEXIBLE = "non-flexible"


class IsmItem(Base):
    """Model for storing ism (word) morphology data."""

    __tablename__ = "isms"

    ism = Column(String(255), primary_key=True)
    status = Column(String(50), nullable=False)
    number = Column(String(50), nullable=False)
    gender = Column(String(50), nullable=False)
    heaviness = Column(Enum(HeavinessEnum), nullable=False)
    ism_type = Column(Enum(IsmTypeEnum))  # Renamed from 'type' to avoid duplicate
    flexibility = Column(Enum(FlexibilityEnum))
    root = Column(String(255))
    lem = Column(String(255))
    chapter = Column(Integer, nullable=False)
    verse = Column(Integer, nullable=False)
    word_num = Column(Integer, nullable=False)
    token = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Ism {self.ism}:{self.status}:{self.number}:{self.gender}:{self.ism_type}>"
