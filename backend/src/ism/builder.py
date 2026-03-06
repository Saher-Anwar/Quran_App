"""IsmBuilder class for building isms database from morphology file."""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.ism.models import IsmItem, HeavinessEnum, IsmTypeEnum, FlexibilityEnum, GenderEnum, NumberEnum

logger = logging.getLogger(__name__)


class IsmBuilder:
    """Builder class for parsing and inserting ism data into database."""

    def __init__(self, db: AsyncSession):
        """Initialize the builder with a database session."""
        self.db = db

    @staticmethod
    def parse_line(line: str) -> dict | None:
        """
        Parses a line of text into an ism dictionary.

        Args:
            line (str): The line of text to be parsed.

        Returns:
            dict | None: Dictionary containing ism data, or None if not an ism.
        """
        parsed_line = line.split()
        if len(parsed_line) < 4:
            return None

        if not parsed_line or not IsmBuilder.is_ism(parsed_line[2], parsed_line[3]):
            return None

        description = IsmBuilder.extract_description(parsed_line[3])
        ism = IsmBuilder.parse_description(description)

        ism.update(IsmBuilder.extract_location(parsed_line[0]))
        ism["ism"] = parsed_line[1]

        return ism

    @staticmethod
    def extract_location(location: str) -> dict:
        """
        Parses a location string into a dictionary.

        Args:
            location (str): The location string to be parsed (e.g., "1:1:1:1").

        Returns:
            dict: Dictionary with chapter, verse, word_num, token.
        """
        res = location.split(":")
        return {
            "chapter": int(res[0]),
            "verse": int(res[1]),
            "word_num": int(res[2]),
            "token": int(res[3])
        }

    @staticmethod
    def is_ism(tag_segment: str, desc_segment: str) -> bool:
        """
        Checks if the word is an ism (noun).

        Args:
            tag_segment (str): The tag segment.
            desc_segment (str): The description segment.

        Returns:
            bool: True if the word is an ism, False otherwise.
        """
        if "PN" in desc_segment:
            return True

        return False if "ROOT" not in desc_segment or tag_segment != "N" else True

    @staticmethod
    def extract_description(description: str) -> list[str]:
        """
        Segments a description string into a list of strings using '|' as the splitter.

        Args:
            description (str): The description string to be parsed.

        Returns:
            list[str]: A list of strings representing the description.
        """
        return description.split("|")

    @staticmethod
    def parse_description(segments: list[str]) -> dict:
        """
        Iterates over each segment and parses it accordingly.

        Args:
            segments (list[str]): The segments to be parsed.

        Returns:
            dict: A dictionary containing the root word, lemma, and properties of an ism.
        """
        res = {}
        cases = ["NOM", "ACC", "GEN"]
        # Default values with uppercase enum values
        res['status'] = "NOM"
        res["gender"] = "MASCULINE"
        res["number"] = "SINGULAR"
        res["ism_type"] = "PROPER"
        res["root"] = None
        res["lem"] = None
        res["heaviness"] = None
        res["flexibility"] = None

        for segment in segments:
            if "ROOT" in segment:
                res["root"] = segment.split(":")[1]
            elif "LEM" in segment:
                res["lem"] = segment.split(":")[1]
            elif segment in cases:
                res["status"] = segment
            elif "INDEF" in segment:
                res["ism_type"] = "COMMON"
            else:
                temp = IsmBuilder.extract_gender_number(segment)
                if temp:
                    gender_code, number_code = temp
                    # Map codes to uppercase full names
                    res["gender"] = "MASCULINE" if gender_code == "M" else "FEMININE"
                    if number_code == "S":
                        res["number"] = "SINGULAR"
                    elif number_code == "D":
                        res["number"] = "DUAL"
                    elif number_code == "P":
                        res["number"] = "PLURAL"

        return res

    @staticmethod
    def extract_gender_number(segment: str) -> tuple[str, str] | None:
        """
        Extracts the gender and number from a segment string.

        Args:
            segment (str): The segment string to be parsed.

        Returns:
            tuple[str, str] | None: Tuple of (gender, number) or None if not found.
        """
        # Possible values = "M", "F", "MD", "FD", "MP", "FP"
        if segment not in ["M", "F", "MD", "FD", "MP", "FP"]:
            return None

        gender = 'M' if 'M' in segment else 'F'
        number = None

        if 'P' in segment:
            number = 'P'
        elif 'D' in segment:
            number = 'D'
        else:
            number = 'S'

        return None if not gender or not number else (gender, number)

    async def build_database(self, file_path: str, batch_size: int = 1000) -> dict:
        """
        Build isms database from morphology file using batch inserts.

        Args:
            file_path: Path to the morphology text file
            batch_size: Number of records to insert per batch (default: 1000)

        Returns:
            dict: Summary of the build operation
        """
        total_inserted = 0
        skipped = 0
        duplicates = 0
        batch = []
        seen_isms = set()

        # Load existing isms from database to check for duplicates
        logger.info("Loading existing isms from database...")
        result = await self.db.execute(select(IsmItem.ism))
        existing_isms = {row[0] for row in result.fetchall()}
        logger.info(f"Found {len(existing_isms)} existing isms in database")

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    parsed_ism = self.parse_line(line)

                    if not parsed_ism:
                        skipped += 1
                        continue

                    # Check if ism already exists in database or in current batch
                    ism_word = parsed_ism["ism"]
                    if ism_word in existing_isms or ism_word in seen_isms:
                        duplicates += 1
                        continue

                    try:
                        # Create IsmItem instance
                        ism_item = IsmItem(
                            ism=ism_word,
                            status=parsed_ism["status"],
                            number=NumberEnum(parsed_ism["number"]),
                            gender=GenderEnum(parsed_ism["gender"]),
                            heaviness=HeavinessEnum(parsed_ism["heaviness"]) if parsed_ism.get("heaviness") else None,
                            ism_type=IsmTypeEnum(parsed_ism["ism_type"]) if parsed_ism.get("ism_type") else None,
                            flexibility=FlexibilityEnum(parsed_ism["flexibility"]) if parsed_ism.get("flexibility") else None,
                            root=parsed_ism.get("root"),
                            lem=parsed_ism.get("lem"),
                            chapter=parsed_ism["chapter"],
                            verse=parsed_ism["verse"],
                            word_num=parsed_ism["word_num"],
                            token=parsed_ism["token"]
                        )

                        batch.append(ism_item)
                        seen_isms.add(ism_word)

                        # Insert batch when it reaches batch_size
                        if len(batch) >= batch_size:
                            self.db.add_all(batch)
                            await self.db.commit()
                            total_inserted += len(batch)
                            logger.info(f"Processed {line_num} lines: {total_inserted} inserted, {duplicates} duplicates, {skipped} skipped")
                            batch = []

                    except (ValueError, KeyError) as e:
                        logger.error(f"Error processing line {line_num}: {e}")
                        skipped += 1
                        continue
                    except Exception as e:
                        logger.error(f"Unexpected error at line {line_num}: {e}")
                        skipped += 1
                        continue

                # Insert remaining items in batch
                if batch:
                    self.db.add_all(batch)
                    await self.db.commit()
                    total_inserted += len(batch)

            logger.info(f"✓ Successfully inserted {total_inserted} ism items")
            logger.info(f"✗ Skipped {duplicates} duplicates")
            if skipped > 0:
                logger.warning(f"✗ Skipped {skipped} invalid/error lines")

            return {
                "total_inserted": total_inserted,
                "duplicates": duplicates,
                "skipped": skipped
            }

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Fatal error: {e}")
            logger.error(f"Partial completion: {total_inserted} items inserted before error")
            raise
