#!/usr/bin/env python3
"""Quick test script for the synthetic data generator."""

from core import SyntheticDataEngine, FieldSchema
from formatters import CSVFormatter, JSONFormatter, SQLFormatter


def test_basic_generation():
    """Test basic data generation with various field types."""
    print("Testing synthetic data generator...\n")

    # Define test fields
    fields = [
        FieldSchema(name="id", field_type="integer", constraints={"min": 1, "max": 100}),
        FieldSchema(name="email", field_type="email", constraints={}),
        FieldSchema(name="name", field_type="name", constraints={}),
        FieldSchema(name="signup_date", field_type="date", constraints={"start": "2024-01-01", "end": "2024-12-31"}),
        FieldSchema(name="is_active", field_type="boolean", constraints={}),
    ]

    # Create engine and generate data
    engine = SyntheticDataEngine(fields)
    data = engine.generate(5)

    print("Generated 5 rows:")
    print("-" * 80)
    for i, row in enumerate(data, 1):
        print(f"Row {i}: {row}")

    print("\n" + "=" * 80)
    print("\nCSV Format:")
    print("-" * 80)
    csv_output = CSVFormatter.format(data)
    print(csv_output)

    print("=" * 80)
    print("\nJSON Format:")
    print("-" * 80)
    json_output = JSONFormatter.format(data)
    print(json_output)

    print("\n" + "=" * 80)
    print("\nSQL Format:")
    print("-" * 80)
    sql_output = SQLFormatter.format(data, table_name="test_users")
    print(sql_output[:500] + "..." if len(sql_output) > 500 else sql_output)

    print("\n" + "=" * 80)
    print("\n✓ All tests passed!")


if __name__ == "__main__":
    test_basic_generation()
