"""API routes for Verse endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.verse.schemas import VerseCreate, VerseResponse
from src.verse.service import VerseService

router = APIRouter()


@router.post("/", response_model=VerseResponse, status_code=status.HTTP_201_CREATED)
async def create_verse(
    verse_data: VerseCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new verse.

    Args:
        verse_data: Verse data including surah number, verse number, Arabic text, and translations
        db: Database session

    Returns:
        Created verse with ID and timestamps
    """
    # Check if verse already exists
    existing_verse = await VerseService.get_verse_by_reference(
        db,
        verse_data.surah_number,
        verse_data.verse_number
    )
    if existing_verse:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Verse {verse_data.surah_number}:{verse_data.verse_number} already exists"
        )

    verse = await VerseService.create_verse(db, verse_data)
    return verse


@router.get("/{verse_id}", response_model=VerseResponse)
async def get_verse(
    verse_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a verse by its ID.

    Args:
        verse_id: ID of the verse to retrieve
        db: Database session

    Returns:
        Verse data with Arabic text and translations
    """
    verse = await VerseService.get_verse_by_id(db, verse_id)
    if not verse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Verse with ID {verse_id} not found"
        )
    return verse


@router.get("/reference/{surah_number}/{verse_number}", response_model=VerseResponse)
async def get_verse_by_reference(
    surah_number: int,
    verse_number: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a verse by surah and verse number.

    Args:
        surah_number: Surah number (1-114)
        verse_number: Verse number within the surah
        db: Database session

    Returns:
        Verse data with Arabic text and translations
    """
    verse = await VerseService.get_verse_by_reference(db, surah_number, verse_number)
    if not verse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Verse {surah_number}:{verse_number} not found"
        )
    return verse
