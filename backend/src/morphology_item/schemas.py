"""Pydantic schemas for Morphology Item API."""
from typing import Optional
from pydantic import BaseModel, Field


class MorphologyItemBase(BaseModel):
    """Base schema for Morphology Item."""
    chapter: int = Field(..., ge=1, le=114, description="Chapter number (1-114)")
    verse: int = Field(..., ge=1, description="Verse number within the chapter")
    word_num: int = Field(..., ge=1, description="Word number within the verse")
    token: int = Field(..., ge=1, description="Token number within the word")
    word: Optional[str] = Field(None, description="Arabic word")
    tag: str = Field(..., min_length=1, description="Part of speech tag")
    info: str = Field(..., min_length=1, description="Morphological information")


class MorphologyItemCreate(MorphologyItemBase):
    """Schema for creating a new Morphology Item."""
    pass


class MorphologyItemResponse(MorphologyItemBase):
    """Schema for Morphology Item response."""

    class Config:
        from_attributes = True
