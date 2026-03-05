"""API routes for Morphology Item endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.morphology_item.schemas import MorphologyItemCreate, MorphologyItemResponse
from src.morphology_item.service import MorphologyItemService

router = APIRouter()


@router.post("/", response_model=MorphologyItemResponse, status_code=status.HTTP_201_CREATED)
async def create_morphology_item(
    item_data: MorphologyItemCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new morphology item.

    Args:
        item_data: Morphology item data including chapter, verse, word_num, token, word, tag, and info
        db: Database session

    Returns:
        Created morphology item with ID
    """
    # Check if morphology item already exists
    existing_item = await MorphologyItemService.get_morphology_item_by_reference(
        db,
        item_data.chapter,
        item_data.verse,
        item_data.word_num,
        item_data.token
    )
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Morphology item {item_data.chapter}:{item_data.verse}:{item_data.word_num}:{item_data.token} already exists"
        )

    morphology_item = await MorphologyItemService.create_morphology_item(db, item_data)
    return morphology_item


@router.get("/{item_id}", response_model=MorphologyItemResponse)
async def get_morphology_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a morphology item by its ID.

    Args:
        item_id: ID of the morphology item to retrieve
        db: Database session

    Returns:
        Morphology item data with all morphological information
    """
    morphology_item = await MorphologyItemService.get_morphology_item_by_id(db, item_id)
    if not morphology_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Morphology item with ID {item_id} not found"
        )
    return morphology_item


@router.get("/reference/{chapter}/{verse}/{word_num}/{token}", response_model=MorphologyItemResponse)
async def get_morphology_item_by_reference(
    chapter: int,
    verse: int,
    word_num: int,
    token: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a morphology item by chapter, verse, word_num, and token.

    Args:
        chapter: Chapter number (1-114)
        verse: Verse number within the chapter
        word_num: Word number within the verse
        token: Token number within the word
        db: Database session

    Returns:
        Morphology item data with all morphological information
    """
    morphology_item = await MorphologyItemService.get_morphology_item_by_reference(
        db, chapter, verse, word_num, token
    )
    if not morphology_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Morphology item {chapter}:{verse}:{word_num}:{token} not found"
        )
    return morphology_item
