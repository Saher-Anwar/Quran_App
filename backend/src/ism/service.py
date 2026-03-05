"""Business logic for Ism Item operations."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from src.ism.models import IsmItem
from src.ism.schemas import IsmItemCreate


class IsmItemService:
    """Service layer for Ism Item operations."""

    @staticmethod
    async def create_ism_item(
        db: AsyncSession,
        item_data: IsmItemCreate
    ) -> IsmItem:
        """
        Create a new ism item in the database.

        Args:
            db: Database session
            item_data: Ism item data to create

        Returns:
            Created IsmItem object
        """
        ism_item = IsmItem(
            ism=item_data.ism,
            status=item_data.status,
            number=item_data.number,
            gender=item_data.gender,
            heaviness=item_data.heaviness,
            ism_type=item_data.ism_type,
            flexibility=item_data.flexibility,
            root=item_data.root,
            lem=item_data.lem,
            chapter=item_data.chapter,
            verse=item_data.verse,
            word_num=item_data.word_num,
            token=item_data.token
        )
        db.add(ism_item)
        await db.flush()
        await db.refresh(ism_item)
        return ism_item

    @staticmethod
    async def get_ism_item_by_word(
        db: AsyncSession,
        ism: str
    ) -> Optional[IsmItem]:
        """
        Get an ism item by the word itself.

        Args:
            db: Database session
            ism: The Arabic word

        Returns:
            IsmItem object if found, None otherwise
        """
        result = await db.execute(
            select(IsmItem).where(IsmItem.ism == ism)
        )
        return result.scalar_one_or_none()
