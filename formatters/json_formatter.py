"""JSON output formatter."""

import json
from typing import List, Dict, Any


class JSONFormatter:
    """Format synthetic data as JSON."""

    @staticmethod
    def format(data: List[Dict[str, Any]], indent: int = 2) -> str:
        """Format data as JSON string."""
        return json.dumps(data, indent=indent, default=str)

    @staticmethod
    def write_to_file(data: List[Dict[str, Any]], filepath: str, indent: int = 2) -> None:
        """Write data to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=indent, default=str)
