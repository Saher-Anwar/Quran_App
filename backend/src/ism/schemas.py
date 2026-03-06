"""Pydantic schemas for Ism API."""
from typing import Optional
from pydantic import BaseModel, Field

from src.ism.models import HeavinessEnum, IsmTypeEnum, FlexibilityEnum, GenderEnum, NumberEnum


class IsmItemBase(BaseModel):
    """Base schema for Ism Item."""
    ism: str = Field(..., min_length=1, max_length=255, description="The Arabic word")
    status: str = Field(..., min_length=1, max_length=50, description="Grammatical status")
    number: NumberEnum = Field(..., description="Number (SINGULAR, DUAL, PLURAL)")
    gender: GenderEnum = Field(..., description="Gender (MASCULINE, FEMININE)")
    heaviness: Optional[HeavinessEnum] = Field(None, description="Heaviness (LIGHT or HEAVY)")
    ism_type: Optional[IsmTypeEnum] = Field(None, description="Type (PROPER or COMMON)")
    flexibility: Optional[FlexibilityEnum] = Field(None, description="Flexibility (FLEXIBLE, PARTIAL, or NON_FLEXIBLE)")
    root: Optional[str] = Field(None, max_length=255, description="Root word")
    lem: Optional[str] = Field(None, max_length=255, description="Lemma")
    chapter: int = Field(..., ge=1, le=114, description="Chapter number (1-114)")
    verse: int = Field(..., ge=1, description="Verse number")
    word_num: int = Field(..., ge=1, description="Word number within the verse")
    token: int = Field(..., ge=1, description="Token number within the word")


class IsmItemCreate(IsmItemBase):
    """Schema for creating a new Ism Item."""
    pass


class IsmItemResponse(IsmItemBase):
    """Schema for Ism Item response."""

    class Config:
        from_attributes = True
