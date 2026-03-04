"""Pydantic schemas for Verse API."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class VerseBase(BaseModel):
    """Base schema for Verse."""
    surah_number: int = Field(..., ge=1, le=114, description="Surah number (1-114)")
    verse_number: int = Field(..., ge=1, description="Verse number within the surah")
    text_arabic: str = Field(..., min_length=1, description="Arabic text with diacritics")
    text_simple: Optional[str] = Field(None, description="Simplified Arabic text without diacritics")
    translation_english: Optional[str] = Field(None, description="English translation")


class VerseCreate(VerseBase):
    """Schema for creating a new Verse."""
    pass


class VerseResponse(VerseBase):
    """Schema for Verse response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
