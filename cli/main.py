#!/usr/bin/env python3
"""Command-line interface for synthetic data generator."""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import SyntheticDataEngine, FieldSchema
from formatters import CSVFormatter, JSONFormatter, SQLFormatter


def get_field_constraints(field_type: str) -> dict:
    """Interactively gather constraints for a field type."""
    constraints = {}

    if field_type == 'integer':
        min_val = input("  Min value (default 0): ").strip()
        max_val = input("  Max value (default 1000): ").strip()
        if min_val:
            constraints['min'] = int(min_val)
        if max_val:
            constraints['max'] = int(max_val)

    elif field_type == 'float':
        min_val = input("  Min value (default 0.0): ").strip()
        max_val = input("  Max value (default 1000.0): ").strip()
        precision = input("  Decimal precision (default 2): ").strip()
        if min_val:
            constraints['min'] = float(min_val)
        if max_val:
            constraints['max'] = float(max_val)
        if precision:
            constraints['precision'] = int(precision)

    elif field_type == 'string':
        length = input("  Length (default 10): ").strip()
        if length:
            constraints['length'] = int(length)

    elif field_type == 'date':
        start = input("  Start date (YYYY-MM-DD, default 2020-01-01): ").strip()
        end = input("  End date (YYYY-MM-DD, default 2024-12-31): ").strip()
        if start:
            constraints['start'] = start
        if end:
            constraints['end'] = end

    elif field_type == 'datetime':
        start = input("  Start datetime (YYYY-MM-DD HH:MM:SS, default 2020-01-01 00:00:00): ").strip()
        end = input("  End datetime (YYYY-MM-DD HH:MM:SS, default 2024-12-31 23:59:59): ").strip()
        if start:
            constraints['start'] = start
        if end:
            constraints['end'] = end

    elif field_type == 'email':
        domain = input("  Email domain (optional, e.g., company.com): ").strip()
        if domain:
            constraints['domain'] = domain

    elif field_type == 'name':
        name_type = input("  Name type (full/first/last, default full): ").strip()
        if name_type:
            constraints['type'] = name_type

    elif field_type == 'boolean':
        prob = input("  Probability of TRUE (0.0-1.0, default 0.5): ").strip()
        if prob:
            constraints['true_probability'] = float(prob)

    return constraints


def interactive_field_setup() -> list:
    """Interactively configure fields."""
    print("\nSupported field types:")
    print("  integer, float, string, email, phone, date, datetime, boolean")
    print("  uuid, name, address, city, country, company, url")
    print()

    num_fields = 0
    while num_fields < 1 or num_fields > 10:
        try:
            num_fields = int(input("How many fields? (1-10): ").strip())
            if num_fields < 1 or num_fields > 10:
                print("Please enter a number between 1 and 10")
        except ValueError:
            print("Please enter a valid number")

    fields = []
    for i in range(num_fields):
        print(f"\nField {i + 1}:")
        name = input("  Name: ").strip()
        while not name:
            print("  Field name cannot be empty")
            name = input("  Name: ").strip()

        field_type = input("  Type: ").strip().lower()

        valid_types = [
            'integer', 'float', 'string', 'email', 'phone',
            'date', 'datetime', 'boolean', 'uuid', 'name',
            'address', 'city', 'country', 'company', 'url'
        ]

        while field_type not in valid_types:
            print(f"  Invalid type. Choose from: {', '.join(valid_types)}")
            field_type = input("  Type: ").strip().lower()

        constraints = get_field_constraints(field_type)

        fields.append(FieldSchema(name=name, field_type=field_type, constraints=constraints))

    return fields


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generate synthetic data with customizable fields',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli/main.py --rows 100 --output data.csv --format csv
  python cli/main.py --rows 50 --output users.json --format json
  python cli/main.py --rows 200 --output insert.sql --format sql --table users
        """
    )

    parser.add_argument('-r', '--rows', type=int, required=True,
                        help='Number of rows to generate (1-1000)')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='Output file path')
    parser.add_argument('-f', '--format', type=str, choices=['csv', 'json', 'sql'],
                        default='csv', help='Output format (default: csv)')
    parser.add_argument('-t', '--table', type=str, default='synthetic_data',
                        help='Table name for SQL format (default: synthetic_data)')

    args = parser.parse_args()

    # Validate row count
    if args.rows < 1 or args.rows > 1000:
        print("Error: Number of rows must be between 1 and 1000")
        sys.exit(1)

    # Interactive field setup
    try:
        fields = interactive_field_setup()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError during field setup: {e}")
        sys.exit(1)

    # Generate data
    print(f"\nGenerating {args.rows} rows...")
    try:
        engine = SyntheticDataEngine(fields)
        data = engine.generate(args.rows)
        print(f"✓ Generated {len(data)} rows")
    except Exception as e:
        print(f"Error generating data: {e}")
        sys.exit(1)

    # Write output
    print(f"Writing to {args.output}...")
    try:
        if args.format == 'csv':
            CSVFormatter.write_to_file(data, args.output)
        elif args.format == 'json':
            JSONFormatter.write_to_file(data, args.output)
        elif args.format == 'sql':
            SQLFormatter.write_to_file(data, args.output, args.table)

        print(f"✓ Output saved to {args.output}")
    except Exception as e:
        print(f"Error writing output: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
