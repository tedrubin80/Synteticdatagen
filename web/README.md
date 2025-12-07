# SynGen Pro - Web Interface

A professional, full-featured web application for the SynGen synthetic data generator. Built with Flask and Bootstrap 5, this web interface provides an intuitive way to generate synthetic data through a modern UI or REST API.

## Features

### User Management
- **User Registration & Authentication** - Secure account creation with email validation
- **Profile Management** - View usage statistics, manage API keys
- **Session Management** - Persistent login with "Remember Me" functionality

### Data Generation
- **Interactive UI** - Visual field configuration with real-time preview
- **15+ Data Types** - Support for integers, floats, strings, emails, names, addresses, dates, and more
- **Flexible Constraints** - Configure min/max values, date ranges, string lengths
- **Multiple Output Formats** - Export as JSON, CSV, or SQL INSERT statements
- **Batch Generation** - Generate up to 100,000 rows per request

### API Access
- **RESTful API** - Programmatic access for automation and integration
- **API Key Authentication** - Secure, regenerable API keys per user
- **Comprehensive Documentation** - Full API docs with examples in Python, JavaScript, and cURL

### Usage Tracking
- **Request History** - View all past data generations
- **Usage Statistics** - Track daily and total request counts
- **Rate Limiting** - Fair usage limits to ensure service availability

## Quick Start

### Prerequisites

- Python 3.10+
- pip (Python package manager)

### Installation

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone https://github.com/tedrubin80/Synteticdatagen.git
   cd Synteticdatagen
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the web application**:
   ```bash
   cd web
   python3 app.py
   ```

5. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## Project Structure

```
web/
├── app.py                      # Flask application factory
├── config.py                   # Configuration settings
├── models.py                   # SQLAlchemy database models
├── forms.py                    # WTForms form definitions
├── syngen.db                   # SQLite database (created on first run)
│
├── blueprints/                 # Flask blueprints (route handlers)
│   ├── __init__.py
│   ├── main.py                 # Home, dashboard, pricing routes
│   ├── auth.py                 # Authentication routes
│   ├── generator.py            # Data generation routes
│   └── api_docs.py             # Documentation routes
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Base template with navigation
│   ├── index.html              # Landing page
│   ├── dashboard.html          # User dashboard
│   ├── pricing.html            # Pricing information
│   ├── auth/
│   │   ├── login.html          # Login page
│   │   ├── register.html       # Registration page
│   │   └── profile.html        # User profile page
│   ├── generator/
│   │   ├── index.html          # Data generator UI
│   │   └── history.html        # Generation history
│   └── docs/
│       ├── index.html          # API documentation overview
│       ├── authentication.html # Auth documentation
│       ├── endpoints.html      # API endpoints reference
│       └── examples.html       # Code examples
│
└── static/
    └── css/
        └── style.css           # Custom styles
```

## Pages & Routes

| Route | Description | Auth Required |
|-------|-------------|---------------|
| `/` | Landing page with features overview | No |
| `/auth/register` | Create a new account | No |
| `/auth/login` | Sign in to existing account | No |
| `/auth/logout` | Sign out | Yes |
| `/auth/profile` | View profile and API key | Yes |
| `/dashboard` | User dashboard with stats | Yes |
| `/generator/` | Interactive data generator | Yes |
| `/generator/history` | View generation history | Yes |
| `/docs/` | API documentation | No |
| `/docs/authentication` | API auth documentation | No |
| `/docs/endpoints` | API endpoints reference | No |
| `/docs/examples` | Code examples | No |
| `/pricing` | Service information | No |

## Configuration

The application can be configured through environment variables or by modifying `config.py`:

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key for sessions | Auto-generated |
| `DATABASE_URL` | Database connection string | `sqlite:///syngen.db` |
| `FREE_TIER_LIMIT` | Daily request limit | 100 |
| `MAX_ROWS_FREE` | Max rows per request | 1,000 |

### Production Configuration

For production deployment, set these environment variables:

```bash
export SECRET_KEY="your-secure-random-key"
export DATABASE_URL="postgresql://user:pass@host/dbname"  # Optional: use PostgreSQL
```

## Supported Data Types

| Type | Description | Constraints |
|------|-------------|-------------|
| `integer` | Random integer | `min`, `max` |
| `float` | Random decimal number | `min`, `max`, `precision` |
| `string` | Random alphanumeric string | `min_length`, `max_length` |
| `name` | Realistic person name | - |
| `email` | Valid email address | - |
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

## API Usage

### Authentication

All API requests require an API key in the Authorization header:

```bash
Authorization: Bearer YOUR_API_KEY
```

Get your API key from the Profile page after creating an account.

### Generate Data

```bash
curl -X POST http://localhost:5000/generator/generate \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "rows": 100,
    "format": "json",
    "fields": [
      {"name": "id", "type": "integer", "constraints": {"min": 1, "max": 10000}},
      {"name": "name", "type": "name"},
      {"name": "email", "type": "email"},
      {"name": "signup_date", "type": "date", "constraints": {"start": "2024-01-01", "end": "2024-12-31"}}
    ]
  }'
```

### Python Example

```python
import requests

API_KEY = "your_api_key"
URL = "http://localhost:5000/generator/generate"

response = requests.post(URL,
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    json={
        "rows": 50,
        "format": "csv",
        "fields": [
            {"name": "user_id", "type": "uuid"},
            {"name": "username", "type": "name"},
            {"name": "email", "type": "email"},
            {"name": "active", "type": "boolean"}
        ]
    }
)

print(response.json()["data"])
```

## Database

The application uses SQLite by default, which requires no additional setup. The database file (`syngen.db`) is created automatically on first run.

### Database Models

- **User** - Stores user accounts, credentials, and API keys
- **GenerationHistory** - Tracks all data generation requests

### Switching to PostgreSQL

For production, you may want to use PostgreSQL:

1. Install the PostgreSQL adapter:
   ```bash
   pip install psycopg2-binary
   ```

2. Set the database URL:
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost/syngen"
   ```

## Development

### Running in Debug Mode

```bash
cd web
FLASK_DEBUG=1 python3 app.py
```

### Running Tests

```bash
python3 -m pytest tests/
```

## Deployment

### Using Gunicorn (Recommended)

```bash
pip install gunicorn
cd web
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

### Using Docker

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

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## Tech Stack

- **Backend**: Flask 3.x (Python)
- **Database**: SQLAlchemy with SQLite/PostgreSQL
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF with WTForms
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Data Generation**: Faker library

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Acknowledgments

- [Faker](https://faker.readthedocs.io/) - Synthetic data generation
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Bootstrap](https://getbootstrap.com/) - UI framework
- [Bootstrap Icons](https://icons.getbootstrap.com/) - Icon library
