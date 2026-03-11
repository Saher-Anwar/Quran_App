"""API routes for Surah reading view endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.surah.service import SurahService

router = APIRouter()


@router.get("/{chapter}/reading-view")
async def get_surah_reading_view(
    chapter: int,
    start_verse: Optional[int] = Query(None, ge=1, description="Starting verse number for pagination"),
    end_verse: Optional[int] = Query(None, ge=1, description="Ending verse number for pagination"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get surah reading view with morphology, ism properties, and token relationships.

    This endpoint returns complete data for displaying a surah with:
    - All tokens grouped by word and verse
    - Ism properties (status, number, gender, type, etc.) for nouns
    - Token relationship roles (jarr/majroor for Jarr-Majroor, mudaf/idafa for Mudaf-Idafa)

    The frontend can use this data to:
    - Color isms based on their grammatical properties
    - Color tokens within isms based on their relationship roles

    Args:
        chapter: Chapter/Surah number (1-114)
        start_verse: Optional starting verse for pagination (loads entire surah if not specified)
        end_verse: Optional ending verse for pagination
        db: Database session

    Returns:
        Structured reading view data

    Response Example:
        {
          "chapter": 1,
          "verses": [
            {
              "verse": 1,
              "words": [
                {
                  "word_num": 1,
                  "complete_word": "بِسْمِ",
                  "is_ism": true,
                  "ism_properties": {
                    "status": "GEN",
                    "number": "SINGULAR",
                    "gender": "MASCULINE",
                    "ism_type": "PROPER",
                    "heaviness": null,
                    "flexibility": null,
                    "root": "سمو",
                    "lem": "اسْم"
                  },
                  "tokens": [
                    {
                      "token": 1,
                      "text": "بِ",
                      "tag": "PREP",
                      "info": "...",
                      "relationship_role": "jarr"
                    },
                    {
                      "token": 2,
                      "text": "سْمِ",
                      "tag": "N",
                      "info": "...",
                      "relationship_role": "majroor"
                    }
                  ]
                }
              ]
            }
          ]
        }

    Usage Examples:
        GET /api/surahs/1/reading-view              # Load entire Al-Fatiha
        GET /api/surahs/2/reading-view?start_verse=1&end_verse=20   # Load first 20 verses of Al-Baqarah
    """
    if chapter < 1 or chapter > 114:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chapter must be between 1 and 114"
        )

    if start_verse is not None and end_verse is not None:
        if start_verse > end_verse:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_verse must be less than or equal to end_verse"
            )

    try:
        result = await SurahService.get_reading_view(db, chapter, start_verse, end_verse)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve surah reading view: {str(e)}"
        )
