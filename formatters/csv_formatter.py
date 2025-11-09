"""CSV output formatter."""

import csv
from typing import List, Dict, Any
from io import StringIO


class CSVFormatter:
    """Format synthetic data as CSV."""

    @staticmethod
    def format(data: List[Dict[str, Any]]) -> str:
        """Format data as CSV string."""
        if not data:
            return ""

        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

        return output.getvalue()

    @staticmethod
    def write_to_file(data: List[Dict[str, Any]], filepath: str) -> None:
        """Write data to CSV file."""
        if not data:
            return

        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
