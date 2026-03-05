"""Admin utility endpoints - USE WITH CAUTION!"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database import get_db
from src.config import settings

router = APIRouter()


@router.delete("/clear-database")
async def clear_database(
    db: AsyncSession = Depends(get_db),
    confirm: str = None
):
    """
    Clear all data from the database.

    ⚠️ WARNING: This will delete ALL data! Use only in development/testing.

    Args:
        confirm: Must be set to "YES_DELETE_ALL" to proceed
        db: Database session

    Returns:
        Success message with count of deleted records
    """
    # Safety check - only allow in debug/development mode
    if not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available in debug/development mode"
        )

    # Require explicit confirmation
    if confirm != "YES_DELETE_ALL":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide confirm='YES_DELETE_ALL' query parameter"
        )

    try:
        # Get counts before deletion
        verses_result = await db.execute(text("SELECT COUNT(*) FROM verses"))
        verses_count = verses_result.scalar()

        surahs_result = await db.execute(text("SELECT COUNT(*) FROM surahs"))
        surahs_count = surahs_result.scalar()

        # Delete all data
        await db.execute(text("TRUNCATE TABLE verses RESTART IDENTITY CASCADE"))
        await db.execute(text("TRUNCATE TABLE surahs RESTART IDENTITY CASCADE"))
        await db.commit()

        return {
            "message": "Database cleared successfully",
            "deleted": {
                "verses": verses_count,
                "surahs": surahs_count
            }
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear database: {str(e)}"
        )


@router.delete("/clear-verses")
async def clear_verses(
    db: AsyncSession = Depends(get_db),
):
    """
    Clear all verses from the database.

    ⚠️ WARNING: This will delete ALL verses!

    Args:
        db: Database session

    Returns:
        Success message with count of deleted verses
    """
    # Safety check - only allow in debug/development mode
    if not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available in debug/development mode"
        )

    try:
        # Get count before deletion
        result = await db.execute(text("SELECT COUNT(*) FROM verses"))
        count = result.scalar()

        # Delete all verses
        await db.execute(text("TRUNCATE TABLE verses RESTART IDENTITY"))
        await db.commit()

        return {
            "message": "All verses cleared successfully",
            "deleted": count
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear verses: {str(e)}"
        )
