# SynGen - Synthetic Data Generator

A powerful, free tool for generating synthetic data with customizable fields and output formats. Available as a CLI tool, REST API, and full-featured web application.

**100% Free - No Premium Tiers - Open Source**

## Features

- **Interactive Web Interface** - Modern UI built with Flask and Bootstrap 5
- **User Accounts** - Registration, login, API key management
- **CLI Tool** - Command-line interface for scripting and automation
- **REST API** - FastAPI-powered API for programmatic access
- **35+ Data Types** - integers, floats, strings, emails, names, addresses, dates, call center metrics, demographics, and more
- **Multiple Output Formats** - CSV, JSON, or SQL INSERT statements
- **Scalable Generation** - Generate up to 100,000 records per request
- **Kaggle Dataset Cloning** - Learn a real dataset's schema from Kaggle and generate a synthetic clone of it

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/tedrubin80/Synteticdatagen.git
cd Synteticdatagen

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Web Application

```bash
cd web
python3 app.py
```

Open your browser to **http://localhost:5000**

### Run the CLI

```bash
python3 syngen.py --rows 100 --output data.csv --format csv
```

### Run the API Server

```bash
python3 api/app.py
# API available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

## Project Structure

```
Synteticdatagen/
├── core/                    # Core data generation engine
│   ├── engine.py           # Main generation engine
│   ├── schema.py           # Field schema definitions
│   └── generators/         # Data type generators
│
├── formatters/             # Output formatters
│   ├── csv_formatter.py
│   ├── json_formatter.py
│   └── sql_formatter.py
│
├── cli/                    # Command-line interface
│   └── main.py
│
├── api/                    # FastAPI REST API
│   ├── app.py
│   └── models.py
│
├── web/                    # Flask web application
│   ├── app.py              # Flask application
│   ├── config.py           # Configuration
│   ├── models.py           # Database models
│   ├── forms.py            # WTForms
│   ├── blueprints/         # Route handlers
│   ├── templates/          # Jinja2 templates
│   └── static/             # CSS, JS, images
│
├── examples/               # Usage examples
├── requirements.txt        # Python dependencies
└── syngen.py              # CLI convenience wrapper
```

## Supported Data Types

| Type | Description | Constraints |
|------|-------------|-------------|
| `integer` | Random integer | `min`, `max` |
| `float` | Decimal number | `min`, `max`, `precision` |
| `string` | Random string | `min_length`, `max_length` |
| `name` | Person's full name | - |
| `email` | Email address | - |
| `phone` | Phone number | - |
| `company` | Company name | - |
| `address` | Street address | - |
| `city` | City name | - |
| `country` | Country name | - |
| `url` | Website URL | - |
| `date` | Date (YYYY-MM-DD) | `start`, `end` |
| `datetime` | Date and time | `start`, `end` |
| `boolean` | True/False | - |
| `uuid` | UUID v4 | - |
| `category` | Value sampled from a custom list | `choices`, `weights` |

### Call Center Metrics

| Type | Description | Constraints |
|------|-------------|-------------|
| `call_duration` | Call handle time in seconds (right-skewed) | `min`, `max`, `mean` |
| `wait_time` | Time in queue before answer, in seconds | `min`, `max`, `mean` |
| `hold_time` | Time on hold during the call, in seconds | `min`, `max`, `mean` |
| `call_type` | Inbound / Outbound | `choices`, `weights` |
| `call_channel` | Phone / Chat / Email / Social Media | `choices`, `weights` |
| `call_department` | Queue/department that handled the call | `choices`, `weights` |
| `agent_id` | Agent identifier from a bounded roster | `prefix`, `num_agents` |
| `call_priority` | Low / Medium / High / Critical | `choices`, `weights` |
| `call_outcome` | Resolved / Escalated / Abandoned / ... | `choices`, `weights` |
| `resolution_status` | Resolved / Unresolved / Escalated / Pending | `choices`, `weights` |
| `sentiment` | Positive / Neutral / Negative | `choices`, `weights` |
| `csat_score` | Customer satisfaction score (skewed positive) | `scale`, `choices`, `weights` |
| `nps_score` | Net Promoter Score response, 0-10 | `choices`, `weights` |

### Demographics

| Type | Description | Constraints |
|------|-------------|-------------|
| `age` | Age in years, skewed toward working adults | `min`, `max`, `mode` |
| `gender` | Gender identity | `choices`, `weights` |
| `ethnicity` | Race/ethnicity (US Census-style buckets) | `choices`, `weights` |
| `marital_status` | Marital status | `choices`, `weights` |
| `education_level` | Highest education attained | `choices`, `weights` |
| `employment_status` | Employment status | `choices`, `weights` |
| `income_bracket` | Household income bracket label | `choices`, `weights` |
| `household_size` | Number of people in the household | `min`, `max`, `choices`, `weights` |
| `language_preference` | Preferred language | `choices`, `weights` |
| `generation` | Generational cohort (Gen Z, Millennial, ...) | `choices`, `weights` |

Every categorical type above ships with a realistic default distribution but can be fully overridden, e.g.:

```json
{"name": "region", "type": "category", "constraints": {
  "choices": ["West", "Midwest", "South", "Northeast"],
  "weights": [0.24, 0.21, 0.38, 0.17]
}}
```

## Usage Examples

### CLI

```bash
# Generate 100 rows of customer data as CSV
python3 syngen.py --rows 100 --output customers.csv --format csv

# Generate JSON data
python3 syngen.py --rows 50 --output users.json --format json

# Generate SQL INSERT statements
python3 syngen.py --rows 200 --output seed.sql --format sql --table users
```

### Python API Integration

```python
import requests

response = requests.post('http://localhost:8000/generate', json={
    "rows": 100,
    "format": "json",
    "fields": [
        {"name": "id", "type": "integer", "constraints": {"min": 1, "max": 10000}},
        {"name": "name", "type": "name"},
        {"name": "email", "type": "email"},
        {"name": "signup_date", "type": "date", "constraints": {
            "start": "2024-01-01",
            "end": "2024-12-31"
        }}
    ]
})

data = response.json()['data']
```

### cURL

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "rows": 50,
    "format": "csv",
    "fields": [
      {"name": "user_id", "type": "uuid"},
      {"name": "email", "type": "email"},
      {"name": "active", "type": "boolean"}
    ]
  }'
```

### Clone a Real Dataset from Kaggle

Point Syngen at a public Kaggle dataset and it will infer a field schema
(types + realistic distributions per column) and generate a fresh synthetic
clone - the real rows are only used to learn the shape of the data and are
never stored or returned.

You'll need a Kaggle username and API key from
[kaggle.com/settings](https://www.kaggle.com/settings) ("Create New Token").
Credentials are sent per-request only; nothing is persisted server-side.

```bash
# Just learn the schema (no data generated)
curl -X POST http://localhost:8000/kaggle/schema \
  -H "Content-Type: application/json" \
  -d '{
    "kaggle_username": "your_username",
    "kaggle_key": "your_api_key",
    "dataset_ref": "owner/dataset-slug"
  }'

# Learn the schema and generate 500 synthetic rows in one call
curl -X POST http://localhost:8000/kaggle/clone \
  -H "Content-Type: application/json" \
  -d '{
    "kaggle_username": "your_username",
    "kaggle_key": "your_api_key",
    "dataset_ref": "owner/dataset-slug",
    "rows": 500,
    "format": "json"
  }'
```

`/kaggle/search?query=...` is also available to find dataset refs by keyword.
In the web app, use the "Clone Schema from Kaggle Dataset" panel on the
Generator page to search, learn, and populate the field editor in one click.

## Web Application Features

The web interface (`/web`) provides:

- **User Registration & Login** - Create accounts and manage sessions
- **Interactive Generator** - Visual UI to configure fields and generate data
- **API Key Management** - Generate and regenerate API keys
- **Usage Tracking** - View request history and statistics
- **API Documentation** - Built-in docs with code examples

See [web/README.md](web/README.md) for detailed web application documentation.

## Deployment

### Development

```bash
cd web
FLASK_DEBUG=1 python3 app.py
```

### Production with Gunicorn

```bash
pip install gunicorn
cd web
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
WORKDIR /app/web
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

MIT License - See [LICENSE](LICENSE) for details.

## Acknowledgments

- [Faker](https://faker.readthedocs.io/) - Synthetic data generation library
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [FastAPI](https://fastapi.tiangolo.com/) - API framework
- [Bootstrap](https://getbootstrap.com/) - UI framework
