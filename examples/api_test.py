#!/usr/bin/env python3
"""Test script for Syngen API."""

import requests
import json

API_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_field_types():
    """Test field types endpoint."""
    print("Testing field types endpoint...")
    response = requests.get(f"{API_URL}/field-types")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {len(data['field_types'])} field types")
    print("First 3 types:")
    for ft in data['field_types'][:3]:
        print(f"  - {ft['type']}: {ft['description']}")
    print()


def test_generate_json():
    """Test generating JSON data."""
    print("Testing data generation (JSON)...")
    payload = {
        "rows": 5,
        "fields": [
            {"name": "id", "type": "integer", "constraints": {"min": 1, "max": 100}},
            {"name": "email", "type": "email"},
            {"name": "name", "type": "name"},
            {"name": "created_at", "type": "date"}
        ],
        "format": "json"
    }

    response = requests.post(f"{API_URL}/generate", json=payload)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Generated {data['rows_generated']} rows")
        print("First row:")
        print(json.dumps(data['data'][0], indent=2))
    else:
        print(f"Error: {response.json()}")
    print()


def test_generate_csv():
    """Test generating CSV data."""
    print("Testing data generation (CSV)...")
    payload = {
        "rows": 3,
        "fields": [
            {"name": "product_id", "type": "integer", "constraints": {"min": 1, "max": 1000}},
            {"name": "product_name", "type": "string", "constraints": {"length": 15}},
            {"name": "price", "type": "float", "constraints": {"min": 10.0, "max": 500.0, "precision": 2}}
        ],
        "format": "csv"
    }

    response = requests.post(f"{API_URL}/generate", json=payload)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        print("CSV output:")
        print(response.text[:200])  # First 200 chars
    else:
        print(f"Error: {response.json()}")
    print()


def test_preview():
    """Test preview endpoint."""
    print("Testing preview endpoint...")
    payload = {
        "rows": 100,  # Preview will limit to 10
        "fields": [
            {"name": "uuid", "type": "uuid"},
            {"name": "city", "type": "city"},
            {"name": "country", "type": "country"}
        ],
        "format": "json"
    }

    response = requests.post(f"{API_URL}/generate/preview", json=payload)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Preview generated {data['rows_generated']} rows (max 10)")
        print("First row:")
        print(json.dumps(data['data'][0], indent=2))
    else:
        print(f"Error: {response.json()}")
    print()


def main():
    """Run all tests."""
    print("=" * 80)
    print("Syngen API Test Suite")
    print("=" * 80)
    print()

    try:
        test_health()
        test_field_types()
        test_generate_json()
        test_generate_csv()
        test_preview()

        print("=" * 80)
        print("All tests completed!")
        print("=" * 80)

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API server.")
        print("Make sure the API is running: python3 api/app.py")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
