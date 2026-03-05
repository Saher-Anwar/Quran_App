import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import AsyncSessionLocal
from src.morphology_item.models import MorphologyItem


async def build_corpus_database(file_path: str, batch_size: int = 1000):
    """
    Build a corpus database from a text file containing corpus data.

    This function reads a text file specified by file_path, where each line
    contains a corpus data for each word. It directly inserts into the database
    using batch processing for optimal performance.

    Parameters:
    file_path (str): The path to the text file containing corpus data.
    batch_size (int): Number of records to insert in each batch (default: 1000)
    """
    async with AsyncSessionLocal() as db:
        batch = []
        total_inserted = 0
        skipped = 0

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    segments = line.split('\t')
                    if len(segments) < 3:
                        print(f"Skipping invalid line {line_num}: {line.strip()}")
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
                            db.add_all(batch)
                            await db.commit()
                            total_inserted += len(batch)
                            print(f"Inserted {total_inserted} records...")
                            batch = []

                    except (ValueError, IndexError) as e:
                        print(f"Error parsing line {line_num}: {e}")
                        skipped += 1
                        continue

                # Insert remaining items
                if batch:
                    db.add_all(batch)
                    await db.commit()
                    total_inserted += len(batch)

            print(f"\n✓ Successfully inserted {total_inserted} morphology items")
            if skipped > 0:
                print(f"✗ Skipped {skipped} invalid lines")

        except Exception as e:
            await db.rollback()
            print(f"Error: {e}")
            raise


if __name__ == "__main__":
    file_path = "database_builder/quran-morphology.txt"
    print(f"Starting morphology database build from {file_path}...")
    asyncio.run(build_corpus_database(file_path))