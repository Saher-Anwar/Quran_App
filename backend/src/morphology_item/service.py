"""Business logic for Morphology Item operations."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from src.morphology_item.models import MorphologyItem
from src.morphology_item.schemas import MorphologyItemCreate


class MorphologyItemService:
    """Service layer for Morphology Item operations."""

    @staticmethod
    async def create_morphology_item(
        db: AsyncSession,
        item_data: MorphologyItemCreate
    ) -> MorphologyItem:
        """
        Create a new morphology item in the database.

        Args:
            db: Database session
            item_data: Morphology item data to create

        Returns:
            Created MorphologyItem object
        """
        morphology_item = MorphologyItem(
            chapter=item_data.chapter,
            verse=item_data.verse,
            word_num=item_data.word_num,
            token=item_data.token,
            word=item_data.word,
            tag=item_data.tag,
            info=item_data.info
        )
        db.add(morphology_item)
        await db.flush()
        await db.refresh(morphology_item)
        return morphology_item

    @staticmethod
    async def get_morphology_item_by_id(
        db: AsyncSession,
        item_id: int
    ) -> Optional[MorphologyItem]:
        """
        Get a morphology item by its ID.

        Args:
            db: Database session
            item_id: ID of the morphology item to retrieve

        Returns:
            MorphologyItem object if found, None otherwise
        """
        result = await db.execute(
            select(MorphologyItem).where(MorphologyItem.id == item_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_morphology_item_by_reference(
        db: AsyncSession,
        chapter: int,
        verse: int,
        word_num: int,
        token: int
    ) -> Optional[MorphologyItem]:
        """
        Get a morphology item by chapter, verse, word_num, and token.

        Args:
            db: Database session
            chapter: Chapter number
            verse: Verse number
            word_num: Word number
            token: Token number

        Returns:
            MorphologyItem object if found, None otherwise
        """
        result = await db.execute(
            select(MorphologyItem).where(
                MorphologyItem.chapter == chapter,
                MorphologyItem.verse == verse,
                MorphologyItem.word_num == word_num,
                MorphologyItem.token == token
            )
        )
        return result.scalar_one_or_none()
