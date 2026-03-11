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
    """Model for storing ism (word) grammatical properties."""

    __tablename__ = "isms"

    # Primary key: exact word with diacritics
    ism = Column(String(255), primary_key=True)

    # Grammatical properties (all required except heaviness and flexibility)
    status = Column(String(50), nullable=False)
    number = Column(Enum(NumberEnum), nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    ism_type = Column(Enum(IsmTypeEnum), nullable=False)  # Required
    heaviness = Column(Enum(HeavinessEnum))  # Optional
    flexibility = Column(Enum(FlexibilityEnum))  # Optional

    def __repr__(self):
        return f"<Ism {self.ism}:{self.status}:{self.number}:{self.gender}:{self.ism_type}>"
