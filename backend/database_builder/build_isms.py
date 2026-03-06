import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import AsyncSessionLocal
from src.ism.models import IsmItem, HeavinessEnum, IsmTypeEnum, FlexibilityEnum
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

def parse_line(line):
    """
    Parses a line of text into a list of words.

    Args:
        line (str): The line of text to be parsed.

    Returns:
        list: location - word - tag - description.
    """
    parsed_line = line.split()
    if len(parsed_line) < 4:
        return None
    
    if not parsed_line or not is_ism(parsed_line[2], parsed_line[3]):
        return None
    
    description = extract_description(parsed_line[3])
    ism = parse_description(description)

    ism.update(extract_location(parsed_line[0]))
    ism["ism"] = parsed_line[1]  # Changed from "word" to "ism"

    return ism

def extract_location(location):
    """
    Parses a location string into a list of integers.

    Args:
        location (str): The location string to be parsed.

    Returns:
        list: A list of integers representing the location -> chapter - verse - word - token.
    """
    res = location.split(":")
    return {"chapter": int(res[0]), "verse": int(res[1]), "word_num": int(res[2]), "token": int(res[3])}

def is_ism(tag_segment, desc_segment):
    """
    Checks if the word is an ism (interrogative pronoun).

    Returns:
        bool: True if the word is an ism, False otherwise.
    """
    if "PN" in desc_segment:
        return True
    
    return False if "ROOT" not in desc_segment or tag_segment != "N" else True

def extract_description(description):
    """
    Segments a description string into a list of strings using \'|\' as the splitter.

    Args:
        description (str): The description string to be parsed.

    Returns:
        list: A list of strings representing the description.
    """       

    return description.split("|")

def parse_description(segments : list[str]):
    """
    Iterates over each segment and parses it accordingly.

    Args:
        segment (str): The segment string to be parsed.

    Returns:
        JSON: A JSON containing the root word, lemma, and properties of an ism.
    """ 
    res = {}
    cases = ["NOM", "ACC", "GEN"]
    # Default values with full names
    res['status'] = "NOM"
    res["gender"] = "masculine"
    res["number"] = "singular"
    res["ism_type"] = "proper"  # Changed from "type"
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
            res["ism_type"] = "common"  # Changed from "type"
        else:
            temp = extract_gender_number(segment)
            if temp:
                gender_code, number_code = temp
                # Map codes to full names
                res["gender"] = "masculine" if gender_code == "M" else "feminine"
                if number_code == "S":
                    res["number"] = "singular"
                elif number_code == "D":
                    res["number"] = "dual"
                elif number_code == "P":
                    res["number"] = "plural"

    return res

def extract_gender_number(segment):
    """
    Extracts the gender from a segment string.

    Args:
        segment (str): The segment string to be parsed.

    Returns:
        str: The gender extracted from the segment.
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

def parse_file(file_path):
    """
    Parses a file and returns a list of isms.

    Args:
        file_path (str): The path to the file to be parsed.

    Returns:
        list: A list of isms.
    """
    isms = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parsed_line = parse_line(line)
            if parsed_line:
                isms.append(parsed_line)
    return isms

def test_parser():
    sample_text = "47:2:9:1	مُحَمَّدٍ	N	PN|ROOT:حمد|LEM:مُحَمَّد|GEN"
    print(parse_line(sample_text))

async def build_isms_database(file_path: str, batch_size: int = 100):
    """
    Build isms database from morphology file using individual inserts with duplicate checking.

    Args:
        file_path: Path to the morphology text file
        batch_size: Number of records to process before reporting progress
    """
    async with AsyncSessionLocal() as db:
        total_inserted = 0
        skipped = 0
        duplicates = 0

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    parsed_ism = parse_line(line)

                    if not parsed_ism:
                        skipped += 1
                        continue

                    try:
                        # Check if item already exists
                        result = await db.execute(
                            select(IsmItem).where(
                                IsmItem.ism == parsed_ism["ism"]
                            )
                        )
                        existing = result.scalar_one_or_none()

                        if existing:
                            duplicates += 1
                            if line_num % batch_size == 0:
                                print(f"Processed {line_num} lines: {total_inserted} inserted, {duplicates} duplicates, {skipped} skipped")
                            continue

                        # Create IsmItem instance
                        ism_item = IsmItem(
                            ism=parsed_ism["ism"],
                            status=parsed_ism["status"],
                            number=parsed_ism["number"],
                            gender=parsed_ism["gender"],
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

                        db.add(ism_item)
                        await db.commit()
                        total_inserted += 1

                        # Report progress
                        if line_num % batch_size == 0:
                            print(f"Processed {line_num} lines: {total_inserted} inserted, {duplicates} duplicates, {skipped} skipped")

                    except IntegrityError as e:
                        await db.rollback()
                        duplicates += 1
                        print(f"Duplicate at line {line_num}: {parsed_ism.get('ism', 'unknown')}")
                        continue
                    except (ValueError, KeyError) as e:
                        await db.rollback()
                        print(f"Error processing line {line_num}: {e}")
                        skipped += 1
                        continue
                    except Exception as e:
                        await db.rollback()
                        print(f"Unexpected error at line {line_num}: {e}")
                        skipped += 1
                        continue

            print(f"\n✓ Successfully inserted {total_inserted} ism items")
            print(f"✗ Skipped {duplicates} duplicates")
            if skipped > 0:
                print(f"✗ Skipped {skipped} invalid/error lines")

        except Exception as e:
            await db.rollback()
            print(f"Fatal error: {e}")
            # Don't raise - just log and return
            print(f"Partial completion: {total_inserted} items inserted before error")


if __name__ == "__main__":
    file_path = "database_builder/quran-morphology.txt"
    print(f"Starting isms database build from {file_path}...")
    asyncio.run(build_isms_database(file_path))
