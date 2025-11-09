#!/usr/bin/env python3
"""
Example: Integrating Syngen API into your application
This shows how you would call the API from your own app.
"""

import requests
import json


class SyngenClient:
    """Simple client wrapper for Syngen API."""

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def generate_data(self, rows, fields, format="json", table_name="synthetic_data"):
        """
        Generate synthetic data.

        Args:
            rows: Number of rows to generate (1-1000)
            fields: List of field configurations
                    [{"name": "field_name", "type": "field_type", "constraints": {...}}, ...]
            format: Output format ("json", "csv", "sql")
            table_name: Table name for SQL format

        Returns:
            Response data (format depends on 'format' parameter)
        """
        payload = {
            "rows": rows,
            "fields": fields,
            "format": format,
            "table_name": table_name
        }

        response = requests.post(f"{self.base_url}/generate", json=payload)
        response.raise_for_status()

        if format == "json":
            return response.json()
        else:
            return response.text

    def preview_data(self, fields, rows=5):
        """
        Preview data generation (max 10 rows).

        Args:
            fields: List of field configurations
            rows: Number of rows to preview (max 10)

        Returns:
            Preview data as dict
        """
        payload = {
            "rows": min(rows, 10),
            "fields": fields,
            "format": "json"
        }

        response = requests.post(f"{self.base_url}/generate/preview", json=payload)
        response.raise_for_status()
        return response.json()

    def get_field_types(self):
        """Get list of supported field types."""
        response = requests.get(f"{self.base_url}/field-types")
        response.raise_for_status()
        return response.json()


def example_1_generate_test_users():
    """Example 1: Generate test users for your app."""
    print("Example 1: Generating test users for database seeding")
    print("-" * 60)

    client = SyngenClient()

    # Define user schema
    fields = [
        {"name": "user_id", "type": "uuid"},
        {"name": "username", "type": "string", "constraints": {"min_length": 5, "max_length": 15}},
        {"name": "email", "type": "email", "constraints": {"domain": "testapp.com"}},
        {"name": "full_name", "type": "name"},
        {"name": "city", "type": "city"},
        {"name": "is_active", "type": "boolean", "constraints": {"true_probability": 0.85}},
        {"name": "created_at", "type": "datetime"}
    ]

    # Generate data
    result = client.generate_data(rows=10, fields=fields, format="json")
    print(f"Generated {result['rows_generated']} users")
    print("\nFirst 2 users:")
    for user in result['data'][:2]:
        print(json.dumps(user, indent=2))

    print("\n")


def example_2_generate_orders():
    """Example 2: Generate order data for testing."""
    print("Example 2: Generating order data")
    print("-" * 60)

    client = SyngenClient()

    fields = [
        {"name": "order_id", "type": "integer", "constraints": {"min": 10000, "max": 99999}},
        {"name": "customer_email", "type": "email"},
        {"name": "order_total", "type": "float", "constraints": {"min": 10.0, "max": 500.0, "precision": 2}},
        {"name": "order_date", "type": "date", "constraints": {"start": "2024-01-01", "end": "2024-12-31"}},
        {"name": "is_paid", "type": "boolean", "constraints": {"true_probability": 0.9}}
    ]

    result = client.generate_data(rows=5, fields=fields, format="json")
    print(f"Generated {result['rows_generated']} orders")
    print("\nSample orders:")
    for order in result['data']:
        print(f"  Order #{order['order_id']}: ${order['order_total']:.2f} on {order['order_date']}")

    print("\n")


def example_3_preview_before_bulk():
    """Example 3: Preview data before generating bulk."""
    print("Example 3: Previewing data configuration before bulk generation")
    print("-" * 60)

    client = SyngenClient()

    fields = [
        {"name": "product_id", "type": "integer", "constraints": {"min": 1, "max": 10000}},
        {"name": "product_name", "type": "company"},  # Using company name as product name
        {"name": "price", "type": "float", "constraints": {"min": 9.99, "max": 999.99, "precision": 2}},
        {"name": "in_stock", "type": "boolean"}
    ]

    # Preview first
    preview = client.preview_data(fields, rows=3)
    print(f"Preview: {preview['rows_generated']} rows")
    print(json.dumps(preview['data'], indent=2))

    print("\n✓ Configuration looks good! Now generating 1000 rows...")
    # Would then generate full dataset
    # result = client.generate_data(rows=1000, fields=fields, format="csv")

    print("\n")


def example_4_get_field_info():
    """Example 4: Discover available field types."""
    print("Example 4: Discovering available field types")
    print("-" * 60)

    client = SyngenClient()

    field_types = client.get_field_types()
    print(f"Found {len(field_types['field_types'])} field types:\n")

    for ft in field_types['field_types'][:5]:  # Show first 5
        print(f"  {ft['type']}: {ft['description']}")
        if ft['supported_constraints']:
            print(f"    Constraints: {', '.join(ft['supported_constraints'])}")

    print("\n")


def main():
    """Run all examples."""
    print("=" * 80)
    print("Syngen API Integration Examples")
    print("=" * 80)
    print()

    try:
        example_1_generate_test_users()
        example_2_generate_orders()
        example_3_preview_before_bulk()
        example_4_get_field_info()

        print("=" * 80)
        print("All examples completed successfully!")
        print("=" * 80)

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Syngen API")
        print("Make sure the API is running: python3 api/app.py")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
