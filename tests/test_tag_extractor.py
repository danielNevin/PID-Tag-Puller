"""Tests for tag extraction functionality."""

import pytest
from pathlib import Path
from src.pdf_processor.extractor import PDFExtractor
from src.tag_extractor.extractor import TagExtractor


def test_pdf_extractor_with_test_material():
    """Test PDF extraction with the reference P&ID."""
    test_pdf = Path("Test_Material/ST0008_P1011-1_3_WIP.pdf")

    if not test_pdf.exists():
        pytest.skip("Test material not found")

    extractor = PDFExtractor(test_pdf)
    text = extractor.extract_text()

    assert text is not None
    assert len(text) > 0
    assert "VLV" in text  # Should contain valve tags


def test_tag_extraction_with_test_material():
    """Test tag extraction with the reference P&ID."""
    test_pdf = Path("Test_Material/ST0008_P1011-1_3_WIP.pdf")

    if not test_pdf.exists():
        pytest.skip("Test material not found")

    # Extract text
    pdf_extractor = PDFExtractor(test_pdf)
    text = pdf_extractor.extract_text()

    # Extract tags
    tag_extractor = TagExtractor(text)
    tags = tag_extractor.extract_all_tags(deduplicate=True)

    # Verify we found tags
    assert len(tags) > 0

    # Verify we found expected tag types
    tags_str = " ".join(tags)
    assert "VLV" in tags_str  # Should find valve tags
    assert any("STORM_P" in tag for tag in tags)  # Should find pump tags

    # Get summary
    summary = tag_extractor.get_summary()
    assert summary["total_unique"] > 0
    assert summary["valves"] > 0


def test_tag_patterns():
    """Test individual tag pattern matching."""
    from src.tag_extractor.patterns import COMPILED_PATTERNS, is_excluded

    # Test valve pattern
    valve_text = "VLV1001 and VLV2041"
    valve_matches = COMPILED_PATTERNS["valve"].findall(valve_text)
    assert len(valve_matches) == 2
    assert "VLV1001" in valve_matches

    # Test pump pattern
    pump_text = "STORM_P1001-1 and STORM_P1011-1"
    pump_matches = COMPILED_PATTERNS["pump_storm"].findall(pump_text)
    assert len(pump_matches) == 2

    # Test exclusions
    assert is_excluded("ST0008")  # Drawing number
    assert is_excluded("NOTE 1")  # Note reference
    assert not is_excluded("VLV1001")  # Valid tag
