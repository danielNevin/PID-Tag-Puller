"""CSV export functionality for extracted tags."""

from __future__ import annotations

import csv
from pathlib import Path


class CSVExporter:
    """Export tags to CSV format."""

    @staticmethod
    def export_tags(
        tags: list[str],
        output_path: str | Path,
        include_header: bool = True,
        header_name: str = "Tag"
    ) -> None:
        """
        Export tags to a CSV file with a single column.

        Args:
            tags: List of tags to export
            output_path: Path to the output CSV file
            include_header: Whether to include a header row
            header_name: Name of the header column
        """
        output_path = Path(output_path)

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Write header if requested
            if include_header:
                writer.writerow([header_name])

            # Write each tag as a row
            for tag in tags:
                writer.writerow([tag])

    @staticmethod
    def export_tags_with_counts(
        tag_counts: dict[str, int],
        output_path: str | Path,
        include_header: bool = True
    ) -> None:
        """
        Export tags with their occurrence counts to a CSV file.

        Args:
            tag_counts: Dictionary mapping tags to their counts
            output_path: Path to the output CSV file
            include_header: Whether to include a header row
        """
        output_path = Path(output_path)

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Write header if requested
            if include_header:
                writer.writerow(["Tag", "Count"])

            # Sort by tag name
            sorted_tags = sorted(tag_counts.items())

            # Write each tag and count
            for tag, count in sorted_tags:
                writer.writerow([tag, count])
