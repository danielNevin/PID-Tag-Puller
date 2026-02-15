"""Tag extraction from P&ID text content."""

from __future__ import annotations

from collections import Counter
from tag_extractor.patterns import COMPILED_PATTERNS, is_excluded, is_likely_tag


class TagExtractor:
    """Extract equipment, valve, and instrument tags from P&ID text."""

    def __init__(self, text: str):
        """Initialize with text content from PDF."""
        self.text = text
        self.tags = []
        self.tag_counts = Counter()

    def extract_all_tags(self, deduplicate: bool = True) -> list[str]:
        """
        Extract all tags from the text.

        Args:
            deduplicate: If True, return unique tags only. If False, include duplicates.

        Returns:
            list[str]: List of extracted tags
        """
        self.tags = []

        # Extract tags using each pattern
        for tag_type, pattern in COMPILED_PATTERNS.items():
            matches = pattern.findall(self.text)
            for match in matches:
                # Additional validation
                if is_likely_tag(match) and not is_excluded(match):
                    self.tags.append(match)
                    self.tag_counts[match] += 1

        # Special handling for short pump tags (P####) to avoid false positives
        # Only keep if not part of a sheet number pattern
        self.tags = self._filter_short_pump_tags(self.tags)

        if deduplicate:
            # Return unique tags, sorted
            return sorted(set(self.tags))
        else:
            # Return all tags (including duplicates), sorted
            return sorted(self.tags)

    def _filter_short_pump_tags(self, tags: list[str]) -> list[str]:
        """
        Filter out short pump tags (P####) that are likely part of sheet numbers.

        If a P#### tag appears in the context of a sheet number (e.g., "P1011-1"),
        we should exclude it. However, if it appears standalone, it's likely a real pump tag.
        """
        # For now, keep all P#### tags that passed initial validation
        # More sophisticated filtering could check context in the text
        return tags

    def get_tag_counts(self) -> dict[str, int]:
        """Get counts of how many times each tag appears."""
        return dict(self.tag_counts)

    def get_tags_by_type(self) -> dict[str, list[str]]:
        """
        Categorize tags by type.

        Returns:
            dict: Dictionary with tag types as keys and lists of tags as values
        """
        categorized = {
            "pumps": [],
            "valves": [],
            "instruments": [],
            "equipment": [],
            "other": []
        }

        for tag in set(self.tags):
            if tag.startswith("STORM_P") or (tag.startswith("P") and len(tag) == 5):
                categorized["pumps"].append(tag)
            elif tag.startswith("VLV"):
                categorized["valves"].append(tag)
            elif "-" in tag and len(tag.split("-")) >= 3:
                categorized["instruments"].append(tag)
            elif "TRAP" in tag or "TANK" in tag:
                categorized["equipment"].append(tag)
            else:
                categorized["other"].append(tag)

        # Sort each category
        for category in categorized:
            categorized[category].sort()

        return categorized

    def get_summary(self) -> dict[str, int]:
        """
        Get a summary of extracted tags.

        Returns:
            dict: Summary statistics
        """
        tags_by_type = self.get_tags_by_type()

        return {
            "total_unique": len(set(self.tags)),
            "total_instances": len(self.tags),
            "pumps": len(tags_by_type["pumps"]),
            "valves": len(tags_by_type["valves"]),
            "instruments": len(tags_by_type["instruments"]),
            "equipment": len(tags_by_type["equipment"]),
            "other": len(tags_by_type["other"]),
        }
