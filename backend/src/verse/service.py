"""Business logic for Verse operations."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from src.verse.models import Verse
from src.verse.schemas import VerseCreate


class VerseService:
    """Service layer for Verse operations."""

    @staticmethod
    async def create_verse(db: AsyncSession, verse_data: VerseCreate) -> Verse:
        """
        Create a new verse in the database.

        Args:
            db: Database session
            verse_data: Verse data to create

        Returns:
            Created Verse object
        """
        verse = Verse(
            surah_number=verse_data.surah_number,
            verse_number=verse_data.verse_number,
            text_arabic=verse_data.text_arabic,
            text_simple=verse_data.text_simple,
            translation_english=verse_data.translation_english
        )
        db.add(verse)
        await db.flush()
        await db.refresh(verse)
        return verse

    @staticmethod
    async def get_verse_by_id(db: AsyncSession, verse_id: int) -> Optional[Verse]:
        """
        Get a verse by its ID.

        Args:
            db: Database session
            verse_id: ID of the verse to retrieve

        Returns:
            Verse object if found, None otherwise
        """
        result = await db.execute(
            select(Verse).where(Verse.id == verse_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_verse_by_reference(
        db: AsyncSession,
        surah_number: int,
        verse_number: int
    ) -> Optional[Verse]:
        """
        Get a verse by surah and verse number.

        Args:
            db: Database session
            surah_number: Surah number
            verse_number: Verse number

        Returns:
            Verse object if found, None otherwise
        """
        result = await db.execute(
            select(Verse).where(
                Verse.surah_number == surah_number,
                Verse.verse_number == verse_number
            )
        )
        return result.scalar_one_or_none()
