"""IsmBuilder class for building isms database from morphology table."""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.ism.models import IsmItem, IsmTypeEnum, GenderEnum, NumberEnum, HeavinessEnum
from src.morphology_item.models import MorphologyItem
from pyarabic.araby import is_haraka, is_tanwin
logger = logging.getLogger(__name__)


class IsmBuilder:
    """Builder class for extracting and inserting ism data from morphology table."""

    def __init__(self, db: AsyncSession):
        """Initialize the builder with a database session."""
        self.db = db

    @staticmethod
    def parse_info_to_ism(word: str, info: str) -> dict | None:
        """
        Parse morphology info field to extract ism properties.

        Args:
            word: The word text (with diacritics)
            info: Morphological information string (e.g., "ROOT:سمو|LEM:اسْم|M|GEN")

        Returns:
            Dictionary with ism properties or None if cannot parse
        """
        # Split by pipe to get segments
        segments = info.split("|")

        # Default values
        ism_data = {
            "ism": word,
            "status": "NOM",
            "gender": "MASCULINE",
            "number": "SINGULAR",
            "ism_type": "PROPER",
            "heaviness": None,
            "flexibility": None
        }

        cases = ["NOM", "ACC", "GEN"]

        for segment in segments:
            if segment in cases:
                ism_data["status"] = segment
            elif "INDEF" in segment:
                ism_data["ism_type"] = "COMMON"
            else:
                # Check for gender/number codes
                gender_number = IsmBuilder._extract_gender_number(segment)
                if gender_number:
                    gender_code, number_code = gender_number
                    ism_data["gender"] = "MASCULINE" if gender_code == "M" else "FEMININE"
                    if number_code == "S":
                        ism_data["number"] = "SINGULAR"
                    elif number_code == "D":
                        ism_data["number"] = "DUAL"
                    elif number_code == "P":
                        ism_data["number"] = "PLURAL"

        return ism_data

    @staticmethod
    def _extract_gender_number(segment: str) -> tuple[str, str] | None:
        """
        Extract gender and number from a segment string.

        Args:
            segment: The segment string (e.g., "M", "FP", "MD")

        Returns:
            Tuple of (gender, number) or None
        """
        # Possible values = "M", "F", "MD", "FD", "MP", "FP"
        if segment not in ["M", "F", "MD", "FD", "MP", "FP"]:
            return None

        gender = 'M' if 'M' in segment else 'F'

        if 'P' in segment:
            number = 'P'
        elif 'D' in segment:
            number = 'D'
        else:
            number = 'S'

        return (gender, number)

    @staticmethod
    def calculate_heaviness(word: dict) -> HeavinessEnum:
        """
        Calculate heaviness of a word.
        The word is heavy by default. The word is light if it's singular and the last harakah is not tanwin or
        if the word is non-singular and doesn't end in specific ending combinations.

        Args:
            word: Dictionary containing ism data including "ism", "number", and "gender"

        Returns:
            HeavinessEnum: LIGHT or HEAVY
        """
        if word['number'] == 'SINGULAR':
            # For singular: light if last haraka is NOT tanween
            for token in reversed(word["ism"]):
                if is_haraka(token):
                    if is_tanwin(token):
                        return HeavinessEnum.HEAVY
                    else:
                        return HeavinessEnum.LIGHT

        # For non-singular: check ending combinations
        masc_ending_combinations = ['ونَ', 'ينَ', 'انِ', 'ينِ']
        fem_ending_combinations = ['اتٌ', 'اتٍ']

        word_text = word["ism"]

        if word["gender"] == "MASCULINE":
            # If word ends with masculine sound plural/dual endings, return HEAVY
            for ending in masc_ending_combinations:
                if word_text.endswith(ending):
                    return HeavinessEnum.HEAVY
            # Otherwise LIGHT for non-singular masculine
            return HeavinessEnum.LIGHT
        else:
            # If word ends with feminine sound plural endings, return HEAVY
            for ending in fem_ending_combinations:
                if word_text.endswith(ending):
                    return HeavinessEnum.HEAVY
            # Otherwise LIGHT for non-singular feminine
            return HeavinessEnum.LIGHT


    async def build_database(self, batch_size: int = 1000) -> dict:
        """
        Build isms database from morphology table.

        Queries all nouns from morphology table, parses their info field,
        and inserts unique isms into the isms table.

        Args:
            batch_size: Number of records to insert per batch (default: 1000)

        Returns:
            dict: Summary of the build operation
        """
        total_inserted = 0
        skipped = 0
        batch = []
        seen_isms = set()  # Track unique word forms

        logger.info("Querying nouns from morphology table...")

        # Query all nouns from morphology table
        result = await self.db.execute(
            select(MorphologyItem).where(MorphologyItem.tag == "N")
        )
        morphology_nouns = result.scalars().all()

        logger.info(f"Found {len(morphology_nouns)} noun tokens in morphology table")

        try:
            for morph_item in morphology_nouns:
                # Skip if normalized_word is None
                if not morph_item.normalized_word:
                    skipped += 1
                    continue
                
                # Skip pronouns (PRON in info field)
                if "PRON" in morph_item.info:
                    skipped += 1
                    continue
                
                # Include proper nouns
                if "PN" not in morph_item.info and "ROOT" not in morph_item.info:
                    skipped += 1
                    continue
                
                # Skip duplicates (same normalized word form)
                if morph_item.normalized_word in seen_isms:
                    continue

                try:
                    # Parse info to get ism properties (use normalized_word)
                    ism_data = self.parse_info_to_ism(morph_item.normalized_word, morph_item.info)

                    if not ism_data:
                        skipped += 1
                        continue

                    # Calculate heaviness
                    heaviness = self.calculate_heaviness(ism_data)

                    # Create IsmItem with normalized_word as the ism
                    ism_item = IsmItem(
                        ism=ism_data["ism"],
                        status=ism_data["status"],
                        number=NumberEnum(ism_data["number"]),
                        gender=GenderEnum(ism_data["gender"]),
                        ism_type=IsmTypeEnum(ism_data["ism_type"]),
                        heaviness=heaviness,
                        flexibility=None  # Not extracted from current parsing
                    )

                    batch.append(ism_item)
                    seen_isms.add(morph_item.normalized_word)

                    # Insert batch when it reaches batch_size
                    if len(batch) >= batch_size:
                        self.db.add_all(batch)
                        await self.db.commit()
                        total_inserted += len(batch)
                        logger.info(f"Inserted {total_inserted} unique isms...")
                        batch = []

                except (ValueError, KeyError) as e:
                    logger.error(f"Error processing morphology item {morph_item}: {e}")
                    skipped += 1
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error processing {morph_item.word}: {e}")
                    skipped += 1
                    continue

            # Insert remaining items in batch
            if batch:
                self.db.add_all(batch)
                await self.db.commit()
                total_inserted += len(batch)

            logger.info(f"✓ Successfully inserted {total_inserted} unique ism items")
            if skipped > 0:
                logger.warning(f"✗ Skipped {skipped} items")

            return {
                "total_inserted": total_inserted,
                "skipped": skipped
            }

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Fatal error: {e}")
            logger.error(f"Partial completion: {total_inserted} items inserted before error")
            raise
