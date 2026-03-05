"""API routes for Ism Item endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.ism.schemas import IsmItemCreate, IsmItemResponse
from src.ism.service import IsmItemService

router = APIRouter()


@router.post("/", response_model=IsmItemResponse, status_code=status.HTTP_201_CREATED)
async def create_ism_item(
    item_data: IsmItemCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new ism item.

    Args:
        item_data: Ism item data including word, grammatical properties, and location
        db: Database session

    Returns:
        Created ism item
    """
    # Check if ism item already exists
    existing_item = await IsmItemService.get_ism_item_by_word(db, item_data.ism)
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ism item '{item_data.ism}' already exists"
        )

    ism_item = await IsmItemService.create_ism_item(db, item_data)
    return ism_item


@router.get("/{ism}", response_model=IsmItemResponse)
async def get_ism_item(
    ism: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get an ism item by the Arabic word.

    Args:
        ism: The Arabic word to look up
        db: Database session

    Returns:
        Ism item data with all grammatical information
    """
    ism_item = await IsmItemService.get_ism_item_by_word(db, ism)
    if not ism_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ism item '{ism}' not found"
        )
    return ism_item
