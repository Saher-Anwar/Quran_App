"""Tests for build_isms parser and database builder."""
import pytest
from pathlib import Path
import tempfile
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database_builder.build_isms import (
    parse_line,
    extract_location,
    is_ism,
    extract_description,
    parse_description,
    extract_gender_number,
    parse_file
)
from src.ism.models import IsmItem
from sqlalchemy import select


class TestParsingFunctions:
    """Test individual parsing functions."""

    def test_extract_location(self):
        """Test location parsing."""
        location = "47:2:9:1"
        result = extract_location(location)

        assert result == {
            "chapter": 47,
            "verse": 2,
            "word_num": 9,
            "token": 1
        }

    def test_is_ism_with_proper_noun(self):
        """Test ism detection with proper noun (PN)."""
        tag = "N"
        desc = "PN|ROOT:حمد|LEM:محمد|GEN"

        assert is_ism(tag, desc) is True

    def test_is_ism_with_regular_noun(self):
        """Test ism detection with regular noun."""
        tag = "N"
        desc = "ROOT:كتب|LEM:كتاب|NOM"

        assert is_ism(tag, desc) is True

    def test_is_ism_not_noun(self):
        """Test that non-nouns are not identified as isms."""
        tag = "V"
        desc = "IMPF|ROOT:كتب"

        assert is_ism(tag, desc) is False

    def test_is_ism_no_root(self):
        """Test that nouns without ROOT are not identified as isms."""
        tag = "N"
        desc = "LEM:كتاب|NOM"

        assert is_ism(tag, desc) is False

    def test_extract_description(self):
        """Test description segmentation."""
        desc = "PN|ROOT:حمد|LEM:محمد|GEN"
        result = extract_description(desc)

        assert result == ["PN", "ROOT:حمد", "LEM:محمد", "GEN"]

    def test_extract_gender_number_masculine_singular(self):
        """Test masculine singular extraction."""
        segment = "M"
        result = extract_gender_number(segment)

        assert result == ("M", "S")

    def test_extract_gender_number_feminine_singular(self):
        """Test feminine singular extraction."""
        segment = "F"
        result = extract_gender_number(segment)

        assert result == ("F", "S")

    def test_extract_gender_number_masculine_dual(self):
        """Test masculine dual extraction."""
        segment = "MD"
        result = extract_gender_number(segment)

        assert result == ("M", "D")

    def test_extract_gender_number_feminine_plural(self):
        """Test feminine plural extraction."""
        segment = "FP"
        result = extract_gender_number(segment)

        assert result == ("F", "P")

    def test_extract_gender_number_no_match(self):
        """Test when no gender/number is found."""
        segment = "ROOT:كتب"
        result = extract_gender_number(segment)

        assert result is None

    def test_parse_description_proper_noun(self):
        """Test parsing proper noun description."""
        segments = ["PN", "ROOT:حمد", "LEM:محمد", "GEN"]
        result = parse_description(segments)

        assert result["root"] == "حمد"
        assert result["lem"] == "محمد"
        assert result["status"] == "GEN"
        assert result["ism_type"] == "proper"
        assert result["gender"] == "masculine"
        assert result["number"] == "singular"

    def test_parse_description_common_noun(self):
        """Test parsing common noun description."""
        segments = ["INDEF", "ROOT:كتب", "LEM:كتاب", "NOM", "M"]
        result = parse_description(segments)

        assert result["root"] == "كتب"
        assert result["lem"] == "كتاب"
        assert result["status"] == "NOM"
        assert result["ism_type"] == "common"
        assert result["gender"] == "masculine"
        assert result["number"] == "singular"

    def test_parse_description_feminine_plural(self):
        """Test parsing feminine plural."""
        segments = ["ROOT:امن", "LEM:مؤمن", "ACC", "FP"]
        result = parse_description(segments)

        assert result["gender"] == "feminine"
        assert result["number"] == "plural"
        assert result["status"] == "ACC"

    def test_parse_line_proper_noun(self):
        """Test parsing a complete line with proper noun."""
        line = "47:2:9:1\tمُحَمَّدٍ\tN\tPN|ROOT:حمد|LEM:محمد|GEN"
        result = parse_line(line)

        assert result is not None
        assert result["chapter"] == 47
        assert result["verse"] == 2
        assert result["word_num"] == 9
        assert result["token"] == 1
        assert result["ism"] == "مُحَمَّدٍ"
        assert result["root"] == "حمد"
        assert result["lem"] == "محمد"
        assert result["status"] == "GEN"
        assert result["ism_type"] == "proper"

    def test_parse_line_common_noun(self):
        """Test parsing a complete line with common noun."""
        line = "1:1:2:1\tٱلرَّحْمَٰنِ\tN\tROOT:رحم|LEM:رَحْمَٰن|GEN|M"
        result = parse_line(line)

        assert result is not None
        assert result["ism"] == "ٱلرَّحْمَٰنِ"
        assert result["root"] == "رحم"
        assert result["gender"] == "masculine"
        assert result["number"] == "singular"

    def test_parse_line_not_ism(self):
        """Test that non-ism lines return None."""
        line = "1:1:1:1\tبِسْمِ\tP\tPREP"
        result = parse_line(line)

        assert result is None

    def test_parse_line_invalid_format(self):
        """Test that invalid lines return None."""
        line = "invalid line"
        result = parse_line(line)

        assert result is None


class TestFileParser:
    """Test file parsing functionality."""

    def test_parse_file(self):
        """Test parsing a sample file."""
        # Create a temporary file with sample data
        sample_data = """47:2:9:1\tمُحَمَّدٍ\tN\tPN|ROOT:حمد|LEM:محمد|GEN
                          1:1:1:1\tبِسْمِ\tP\tPREP
                          1:1:2:1\tٱلرَّحْمَٰنِ\tN\tROOT:رحم|LEM:رَحْمَٰن|GEN|M
                          2:1:1:1\tالٓمٓ\tINL\tINTJ
                          """

        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as f:
            f.write(sample_data)
            temp_path = f.name

        try:
            isms = parse_file(temp_path)

            # Should only parse 2 isms (skip the preposition and interjection)
            assert len(isms) == 2
            assert isms[0]["ism"] == "مُحَمَّدٍ"
            assert isms[1]["ism"] == "ٱلرَّحْمَٰنِ"
        finally:
            Path(temp_path).unlink()