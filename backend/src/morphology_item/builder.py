"""MorphologyBuilder class for building morphology database from morphology file."""
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from src.morphology_item.models import MorphologyItem

logger = logging.getLogger(__name__)


class MorphologyBuilder:
    """Builder class for parsing and inserting morphology data into database."""

    def __init__(self, db: AsyncSession):
        """Initialize the builder with a database session."""
        self.db = db

    async def build_database(self, file_path: str, batch_size: int = 1000) -> dict:
        """
        Build a corpus database from a text file containing corpus data.

        This function reads a text file specified by file_path, where each line
        contains a corpus data for each word. It directly inserts into the database
        using batch processing for optimal performance.

        Args:
            file_path (str): The path to the text file containing corpus data.
            batch_size (int): Number of records to insert in each batch (default: 1000)

        Returns:
            dict: Summary of the build operation with total_inserted and skipped counts
        """
        batch = []
        total_inserted = 0
        skipped = 0

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    segments = line.split('\t')
                    if len(segments) < 3:
                        logger.warning(f"Skipping invalid line {line_num}: {line.strip()}")
                        skipped += 1
                        continue

                    # Extract common fields
                    try:
                        chapter, verse, word_num, token = segments[0].split(':')

                        # Construct morphology item
                        item = MorphologyItem(
                            chapter=int(chapter),
                            verse=int(verse),
                            word_num=int(word_num),
                            token=int(token),
                            tag=segments[1],
                            info=segments[2]
                        )

                        # Add 'word' field only if there are at least 4 segments
                        if len(segments) >= 4:
                            item.word = segments[1]
                            item.tag = segments[2]
                            item.info = segments[3]

                        batch.append(item)

                        # Insert batch when it reaches batch_size
                        if len(batch) >= batch_size:
                            self.db.add_all(batch)
                            await self.db.commit()
                            total_inserted += len(batch)
                            logger.info(f"Inserted {total_inserted} records...")
                            batch = []

                    except (ValueError, IndexError) as e:
                        logger.error(f"Error parsing line {line_num}: {e}")
                        skipped += 1
                        continue

                # Insert remaining items
                if batch:
                    self.db.add_all(batch)
                    await self.db.commit()
                    total_inserted += len(batch)

            logger.info(f"✓ Successfully inserted {total_inserted} morphology items")
            if skipped > 0:
                logger.warning(f"✗ Skipped {skipped} invalid lines")

            return {
                "total_inserted": total_inserted,
                "skipped": skipped
            }

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error: {e}")
            raise
