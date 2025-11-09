"""SQL INSERT statement formatter."""

from typing import List, Dict, Any


class SQLFormatter:
    """Format synthetic data as SQL INSERT statements."""

    @staticmethod
    def format(data: List[Dict[str, Any]], table_name: str = "synthetic_data") -> str:
        """Format data as SQL INSERT statements."""
        if not data:
            return ""

        output = []
        columns = list(data[0].keys())
        columns_str = ', '.join(columns)

        for row in data:
            values = []
            for col in columns:
                value = row[col]
                if value is None:
                    values.append('NULL')
                elif isinstance(value, bool):
                    values.append('TRUE' if value else 'FALSE')
                elif isinstance(value, (int, float)):
                    values.append(str(value))
                else:
                    # Escape single quotes in strings
                    escaped = str(value).replace("'", "''")
                    values.append(f"'{escaped}'")

            values_str = ', '.join(values)
            output.append(f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str});")

        return '\n'.join(output)

    @staticmethod
    def write_to_file(data: List[Dict[str, Any]], filepath: str, table_name: str = "synthetic_data") -> None:
        """Write data to SQL file."""
        sql_content = SQLFormatter.format(data, table_name)
        with open(filepath, 'w') as f:
            f.write(sql_content)
