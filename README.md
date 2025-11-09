# Syngen - Synthetic Data Generator

A flexible tool for generating synthetic data with customizable fields and output formats. Available as both a CLI tool and REST API.

## Features

- **Interactive field configuration** - Define 1-10 fields with various data types
- **Flexible output formats** - CSV, JSON, or SQL INSERT statements
- **Wide range of data types** - integers, floats, strings, emails, dates, and more
- **Scalable generation** - Generate 1-1000 records
- **REST API** - Integrate into your applications programmatically
- **Future-proof architecture** - Modular design ready for web interface

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### CLI (Command Line)

```bash
python3 cli/main.py --rows 100 --output data.csv --format csv
# or use the convenience wrapper
python3 syngen.py --rows 100 --output data.csv --format csv
```

### API (REST)

```bash
# Start the API server
python3 api/app.py

# API will be available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

See [API_USAGE.md](API_USAGE.md) for detailed API documentation and integration examples.

### Options

- `-r, --rows` - Number of rows to generate (1-1000) **[required]**
- `-o, --output` - Output file path **[required]**
- `-f, --format` - Output format: csv, json, or sql (default: csv)
- `-t, --table` - Table name for SQL format (default: synthetic_data)

### Supported Field Types

- **Numeric**: `integer`, `float`
- **Text**: `string`, `name`, `company`
- **Contact**: `email`, `phone`, `url`
- **Location**: `address`, `city`, `country`
- **Date/Time**: `date`, `datetime`
- **Other**: `boolean`, `uuid`

## Examples

### Generate customer data as CSV
```bash
python cli/main.py --rows 100 --output customers.csv --format csv
```

Interactive prompts:
```
How many fields? (1-10): 3

Field 1:
  Name: customer_id
  Type: integer
  Min value: 1
  Max value: 10000

Field 2:
  Name: email
  Type: email

Field 3:
  Name: signup_date
  Type: date
  Start date: 2024-01-01
  End date: 2024-12-31
```

### Generate user data as JSON
```bash
python cli/main.py --rows 50 --output users.json --format json
```

### Generate SQL INSERT statements
```bash
python cli/main.py --rows 200 --output insert.sql --format sql --table users
```

## Project Structure

```
syngen/
├── core/                    # Business logic (reusable)
│   ├── engine.py           # Main data generation engine
│   ├── schema.py           # Field schema definitions
│   └── generators/         # Data type generators
├── formatters/             # Output formatters
│   ├── csv_formatter.py
│   ├── json_formatter.py
│   └── sql_formatter.py
├── cli/                    # CLI interface
│   └── main.py            # CLI entry point
├── api/                    # REST API interface
│   ├── app.py             # FastAPI application
│   └── models.py          # Request/response models
├── examples/               # Usage examples
├── web/                    # Future web interface
└── requirements.txt
```

## API Integration

Perfect for integrating into your applications:

```python
import requests

# Generate data via API
response = requests.post('http://localhost:8000/generate', json={
    "rows": 100,
    "fields": [
        {"name": "id", "type": "integer", "constraints": {"min": 1, "max": 1000}},
        {"name": "email", "type": "email"},
        {"name": "created_at", "type": "date"}
    ],
    "format": "json"
})

data = response.json()['data']
```

See [API_USAGE.md](API_USAGE.md) for complete documentation and [examples/integrate_example.py](examples/integrate_example.py) for integration patterns.

## Future Enhancements

- Web-based interface
- Configuration file support (YAML/JSON)
- Custom data patterns with regex
- Relationships between fields
- Data validation rules
- Export to databases directly

## License

MIT
