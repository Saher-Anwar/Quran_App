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
    Clear all data from all tables in the database.

    ⚠️ WARNING: This will delete ALL data from ALL tables! Use only in development/testing.

    Args:
        confirm: Must be set to "YES_DELETE_ALL" to proceed
        db: Database session

    Returns:
        Success message with list of cleared tables
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
        # Get all table names from public schema (excluding alembic_version)
        result = await db.execute(text("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename != 'alembic_version'
        """))
        tables = [row[0] for row in result.fetchall()]

        if not tables:
            return {
                "message": "No tables found to clear",
                "cleared_tables": []
            }

        # Get counts before deletion
        table_counts = {}
        for table in tables:
            count_result = await db.execute(text(f"SELECT COUNT(*) FROM {table}"))
            table_counts[table] = count_result.scalar()

        # Truncate all tables
        for table in tables:
            await db.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))

        await db.commit()

        return {
            "message": "Database cleared successfully",
            "cleared_tables": tables,
            "deleted_counts": table_counts
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear database: {str(e)}"
        )


@router.post("/build-morphology")
async def build_morphology(db: AsyncSession = Depends(get_db)):
    """
    Build morphology database from quran-morphology.txt file.

    Uses the MorphologyBuilder class to populate the database.

    Returns:
        Success message with build statistics
    """
    # Safety check - only allow in debug/development mode
    if not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available in debug/development mode"
        )

    try:
        from src.morphology_item.builder import MorphologyBuilder

        builder = MorphologyBuilder(db)
        file_path = "database_builder/quran-morphology.txt"

        print(f"Starting morphology database build from {file_path}...")
        result = await builder.build_database(file_path)

        return {
            "message": "Morphology database built successfully",
            "total_inserted": result["total_inserted"],
            "skipped": result["skipped"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to build morphology database: {str(e)}"
        )


@router.post("/build-isms")
async def build_isms(db: AsyncSession = Depends(get_db)):
    """
    Build isms database from quran-morphology.txt file.

    Uses the IsmBuilder class to populate the database with ism (noun) data.

    Returns:
        Success message with build statistics
    """
    # Safety check - only allow in debug/development mode
    if not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available in debug/development mode"
        )

    try:
        from src.ism.builder import IsmBuilder

        builder = IsmBuilder(db)
        file_path = "database_builder/quran-morphology.txt"

        print(f"Starting isms database build from {file_path}...")
        result = await builder.build_database(file_path)

        return {
            "message": "Isms database built successfully",
            "total_inserted": result["total_inserted"],
            "duplicates": result["duplicates"],
            "skipped": result["skipped"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to build isms database: {str(e)}"
        )
