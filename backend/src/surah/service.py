"""Service for surah reading view with morphology and ism data."""
import logging
from typing import Optional, Dict, Any, List
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.morphology_item.models import MorphologyItem
from src.ism.models import IsmItem

logger = logging.getLogger(__name__)


class SurahService:
    """Service for retrieving surah data with morphology and ism properties."""

    @staticmethod
    async def get_reading_view(
        db: AsyncSession,
        chapter: int,
        start_verse: Optional[int] = None,
        end_verse: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get surah reading view with morphology, ism properties, and token relationships.

        Args:
            db: Database session
            chapter: Chapter number (1-114)
            start_verse: Optional starting verse number
            end_verse: Optional ending verse number

        Returns:
            Structured data for surah reading view
        """
        # Build morphology query
        morph_query = select(MorphologyItem).where(MorphologyItem.chapter == chapter)

        if start_verse is not None and end_verse is not None:
            morph_query = morph_query.where(MorphologyItem.verse.between(start_verse, end_verse))
        elif start_verse is not None:
            morph_query = morph_query.where(MorphologyItem.verse >= start_verse)
        elif end_verse is not None:
            morph_query = morph_query.where(MorphologyItem.verse <= end_verse)

        morph_query = morph_query.order_by(
            MorphologyItem.verse,
            MorphologyItem.word_num,
            MorphologyItem.token
        )

        # Execute morphology query
        morph_result = await db.execute(morph_query)
        morph_items = morph_result.scalars().all()

        if not morph_items:
            return {"chapter": chapter, "verses": []}

        # Get all unique normalized words from morphology items to query isms
        unique_normalized_words = {item.normalized_word for item in morph_items if item.normalized_word}

        # Query isms for these normalized words
        ism_result = await db.execute(
            select(IsmItem).where(IsmItem.ism.in_(unique_normalized_words))
        )
        ism_items = ism_result.scalars().all()

        # Create ism lookup dictionary by normalized_word
        ism_lookup = {ism.ism: ism for ism in ism_items}

        # Structure the data
        return SurahService._structure_reading_view(morph_items, ism_lookup, chapter)

    @staticmethod
    def _structure_reading_view(
        morph_items: List[MorphologyItem],
        ism_lookup: Dict[str, IsmItem],
        chapter: int
    ) -> Dict[str, Any]:
        """
        Structure morphology and ism data for reading view.

        Args:
            morph_items: List of MorphologyItem objects
            ism_lookup: Dictionary mapping normalized_word to IsmItem
            chapter: Chapter number

        Returns:
            Structured reading view data
        """
        verses = defaultdict(lambda: {"verse": 0, "words": {}})

        for item in morph_items:
            verse_num = item.verse
            word_num = item.word_num

            # Initialize verse
            if verses[verse_num]["verse"] == 0:
                verses[verse_num]["verse"] = verse_num

            # Initialize word
            if word_num not in verses[verse_num]["words"]:
                verses[verse_num]["words"][word_num] = {
                    "word_num": word_num,
                    "complete_word": "",
                    "is_ism": False,
                    "ism_properties": None,
                    "tokens": []
                }

            # Add token
            token_data = {
                "token": item.token,
                "text": item.word or "",
                "tag": item.tag,
                "info": item.info,
                "lem": item.lem,
                "root": item.root,
                "relationship_role": None  # Will be set when calculating relationships
            }
            verses[verse_num]["words"][word_num]["tokens"].append(token_data)
            verses[verse_num]["words"][word_num]["complete_word"] += item.word or ""

            # Check if this token is an ism (join on morphology.normalized_word = isms.ism)
            if item.normalized_word and item.normalized_word in ism_lookup:
                ism = ism_lookup[item.normalized_word]
                verses[verse_num]["words"][word_num]["is_ism"] = True
                verses[verse_num]["words"][word_num]["ism_properties"] = {
                    "status": ism.status,
                    "number": ism.number.value if ism.number else None,
                    "gender": ism.gender.value if ism.gender else None,
                    "ism_type": ism.ism_type.value if ism.ism_type else None,
                    "heaviness": ism.heaviness.value if ism.heaviness else None,
                    "flexibility": ism.flexibility.value if ism.flexibility else None
                }

        # Calculate relationships and convert to lists
        verses_list = []
        for verse_num in sorted(verses.keys()):
            verse = verses[verse_num]

            # Convert words dict to list and calculate token relationships
            words_list = []
            for word_num in sorted(verse["words"].keys()):
                word = verse["words"][word_num]
                SurahService._assign_relationship_roles(word["tokens"])
                words_list.append(word)

            verse["words"] = words_list
            verses_list.append(verse)

        return {
            "chapter": chapter,
            "verses": verses_list
        }

    @staticmethod
    def _assign_relationship_roles(tokens: List[Dict[str, Any]]) -> None:
        """
        Assign relationship roles to tokens (jarr/majroor, mudaf/idafa).

        Modifies tokens in place by setting the 'relationship_role' field.

        Args:
            tokens: List of token dictionaries
        """
        for i in range(len(tokens) - 1):
            curr = tokens[i]
            next_token = tokens[i + 1]

            # Jarr-Majroor: Preposition + Noun
            if curr["tag"] == "PREP" and next_token["tag"] == "N":
                curr["relationship_role"] = "jarr"
                next_token["relationship_role"] = "majroor"

            # Mudaf-Idafa: Noun + Noun
            elif curr["tag"] == "N" and next_token["tag"] == "N":
                # Only assign if not already assigned from jarr-majroor
                if curr["relationship_role"] is None:
                    curr["relationship_role"] = "mudaf"
                if next_token["relationship_role"] is None:
                    next_token["relationship_role"] = "idafa"
