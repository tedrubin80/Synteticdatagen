# Syngen API Usage Guide

REST API for generating synthetic data programmatically. Perfect for integrating into other applications.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the API Server
```bash
python3 api/app.py
```

Or using uvicorn directly:
```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### 3. Access Interactive Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### GET `/`
Health check and API info
```bash
curl http://localhost:8000/
```

Response:
```json
{
  "service": "Syngen API",
  "version": "1.0.0",
  "status": "healthy",
  "docs": "/docs"
}
```

### GET `/field-types`
List all supported field types and their constraints

```bash
curl http://localhost:8000/field-types
```

Response:
```json
{
  "field_types": [
    {
      "type": "integer",
      "description": "Random integer within range",
      "supported_constraints": ["min", "max"]
    },
    {
      "type": "email",
      "description": "Random email address",
      "supported_constraints": ["domain"]
    }
    // ... more types
  ]
}
```

### POST `/generate`
Generate synthetic data in specified format

**Request Body:**
```json
{
  "rows": 100,
  "fields": [
    {
      "name": "user_id",
      "type": "integer",
      "constraints": {"min": 1, "max": 10000}
    },
    {
      "name": "email",
      "type": "email",
      "constraints": {}
    },
    {
      "name": "created_at",
      "type": "date",
      "constraints": {
        "start": "2024-01-01",
        "end": "2024-12-31"
      }
    }
  ],
  "format": "json"
}
```

**Response (format=json):**
```json
{
  "success": true,
  "rows_generated": 100,
  "format": "json",
  "data": [
    {
      "user_id": 5432,
      "email": "user@example.com",
      "created_at": "2024-06-15"
    }
    // ... more rows
  ]
}
```

**Response (format=csv):**
Returns CSV file as plain text with `text/csv` content type

**Response (format=sql):**
Returns SQL INSERT statements as plain text

### POST `/generate/preview`
Preview data generation (max 10 rows, always JSON)

Useful for testing field configurations before generating large datasets.

```bash
curl -X POST http://localhost:8000/generate/preview \
  -H "Content-Type: application/json" \
  -d '{
    "rows": 5,
    "fields": [
      {"name": "id", "type": "integer", "constraints": {"min": 1, "max": 100}},
      {"name": "name", "type": "name"}
    ],
    "format": "json"
  }'
```

## Usage Examples

### Example 1: Generate JSON Data

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "rows": 50,
    "fields": [
      {"name": "id", "type": "integer", "constraints": {"min": 1, "max": 1000}},
      {"name": "email", "type": "email"},
      {"name": "company", "type": "company"},
      {"name": "is_active", "type": "boolean"}
    ],
    "format": "json"
  }'
```

### Example 2: Generate CSV Data

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "rows": 100,
    "fields": [
      {"name": "product_id", "type": "integer", "constraints": {"min": 1, "max": 10000}},
      {"name": "product_name", "type": "string", "constraints": {"length": 20}},
      {"name": "price", "type": "float", "constraints": {"min": 9.99, "max": 999.99, "precision": 2}},
      {"name": "created_at", "type": "datetime"}
    ],
    "format": "csv"
  }' > products.csv
```

### Example 3: Generate SQL Inserts

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "rows": 200,
    "fields": [
      {"name": "user_id", "type": "uuid"},
      {"name": "username", "type": "string", "constraints": {"min_length": 5, "max_length": 15}},
      {"name": "email", "type": "email", "constraints": {"domain": "myapp.com"}},
      {"name": "signup_date", "type": "date", "constraints": {"start": "2023-01-01", "end": "2024-12-31"}}
    ],
    "format": "sql",
    "table_name": "users"
  }' > users.sql
```

### Example 4: Python Integration

```python
import requests

# API endpoint
api_url = "http://localhost:8000/generate"

# Request payload
payload = {
    "rows": 100,
    "fields": [
        {"name": "id", "type": "integer", "constraints": {"min": 1, "max": 10000}},
        {"name": "email", "type": "email"},
        {"name": "name", "type": "name"},
        {"name": "city", "type": "city"},
        {"name": "signup_date", "type": "date"}
    ],
    "format": "json"
}

# Make request
response = requests.post(api_url, json=payload)

if response.status_code == 200:
    result = response.json()
    data = result['data']
    print(f"Generated {result['rows_generated']} rows")
    print(data[:3])  # Print first 3 rows
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

### Example 5: JavaScript/Node.js Integration

```javascript
const axios = require('axios');

async function generateData() {
  try {
    const response = await axios.post('http://localhost:8000/generate', {
      rows: 50,
      fields: [
        { name: 'id', type: 'integer', constraints: { min: 1, max: 1000 } },
        { name: 'email', type: 'email' },
        { name: 'company', type: 'company' }
      ],
      format: 'json'
    });

    console.log(`Generated ${response.data.rows_generated} rows`);
    console.log(response.data.data.slice(0, 3)); // First 3 rows
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

generateData();
```

## Field Types Reference

| Type | Description | Constraints |
|------|-------------|-------------|
| `integer` | Random integer | `min`, `max` |
| `float` | Random float | `min`, `max`, `precision` |
| `string` | Random string | `length`, `min_length`, `max_length`, `charset` |
| `email` | Email address | `domain` |
| `phone` | Phone number | `format` |
| `date` | Date | `start`, `end`, `format` |
| `datetime` | DateTime | `start`, `end`, `format` |
| `boolean` | True/False | `true_probability` (0.0-1.0) |
| `uuid` | UUID | `version` |
| `name` | Person name | `type` (full/first/last) |
| `address` | Street address | - |
| `city` | City name | - |
| `country` | Country name | - |
| `company` | Company name | - |
| `url` | URL | - |

## Error Responses

### 400 Bad Request
Invalid field configuration or parameters

```json
{
  "detail": "Invalid field type: invalid_type. Must be one of [...]"
}
```

### 500 Internal Server Error
Server-side error during generation

```json
{
  "detail": "Internal error: ..."
}
```

## API Limits

- **Rows**: 1-1000 per request
- **Fields**: 1-10 per request
- **Preview**: Max 10 rows returned

## Production Deployment

### Using Gunicorn (recommended for production)

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.app:app --bind 0.0.0.0:8000
```

### Using Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t syngen-api .
docker run -p 8000:8000 syngen-api
```

## CORS Configuration

For web applications, you may need to enable CORS. Add to `api/app.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
