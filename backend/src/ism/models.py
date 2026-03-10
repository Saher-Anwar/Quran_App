"""Ism (Word) database model."""
from sqlalchemy import Column, Integer, String, Enum
import enum
from src.database import Base


class HeavinessEnum(enum.Enum):
    """Enum for ism heaviness."""
    LIGHT = "LIGHT"
    HEAVY = "HEAVY"


class IsmTypeEnum(enum.Enum):
    """Enum for ism type."""
    PROPER = "PROPER"
    COMMON = "COMMON"


class FlexibilityEnum(enum.Enum):
    """Enum for ism flexibility."""
    FLEXIBLE = "FLEXIBLE"
    PARTIAL = "PARTIAL"
    NON_FLEXIBLE = "NON_FLEXIBLE"


class GenderEnum(enum.Enum):
    """Enum for ism gender."""
    MASCULINE = "MASCULINE"
    FEMININE = "FEMININE"


class NumberEnum(enum.Enum):
    """Enum for ism number."""
    SINGULAR = "SINGULAR"
    DUAL = "DUAL"
    PLURAL = "PLURAL"


class IsmItem(Base):
    """Model for storing ism (word) morphology data."""

    __tablename__ = "isms"

    # Composite primary key (matches morphology_item structure)
    chapter = Column(Integer, primary_key=True)
    verse = Column(Integer, primary_key=True)
    word_num = Column(Integer, primary_key=True)
    token = Column(Integer, primary_key=True)

    # Ism data
    ism = Column(String(255), index=True, nullable=False)  # Indexed for searching
    status = Column(String(50), nullable=False)
    number = Column(Enum(NumberEnum), nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    heaviness = Column(Enum(HeavinessEnum))  # Optional
    ism_type = Column(Enum(IsmTypeEnum))  # Optional
    flexibility = Column(Enum(FlexibilityEnum))  # Optional
    root = Column(String(255))  # Optional
    lem = Column(String(255))  # Optional

    def __repr__(self):
        return f"<Ism {self.chapter}:{self.verse}:{self.word_num}:{self.token} - {self.ism}:{self.status}>"
