import os
import sys
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

_DEFAULT_SECRET = 'dev-secret-key-change-in-production'
_IS_PRODUCTION = (
    os.environ.get('FLASK_ENV') == 'production'
    or os.environ.get('PRODUCTION') == '1'
    or bool(os.environ.get('RAILWAY_ENVIRONMENT'))
    or bool(os.environ.get('VERCEL'))
)


def _require_production_secret(name: str, value: str | None, default: str) -> str:
    if _IS_PRODUCTION and (not value or value == default):
        print(f'FATAL: {name} must be set in production.', file=sys.stderr)
        sys.exit(1)
    return value or default


def _database_url() -> str:
    """Normalize hosted Postgres URLs (Railway/Vercel often use postgres://)."""
    url = os.environ.get('DATABASE_URL')
    if not url:
        return 'sqlite:///' + os.path.join(basedir, 'syngen.db')
    if url.startswith('postgres://'):
        return 'postgresql://' + url[len('postgres://'):]
    return url


class Config:
    SECRET_KEY = _require_production_secret(
        'SECRET_KEY',
        os.environ.get('SECRET_KEY'),
        _DEFAULT_SECRET,
    )
    # Encrypts secrets stored on a user's behalf (e.g. saved Kaggle API keys).
    # Set this explicitly in production: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    APP_ENCRYPTION_KEY = os.environ.get('APP_ENCRYPTION_KEY')
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = _IS_PRODUCTION
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = _IS_PRODUCTION
    REMEMBER_COOKIE_HTTPONLY = True

    # App settings
    APP_NAME = 'SynGen Pro'
    APP_DESCRIPTION = 'Professional Synthetic Data Generation Service'

    # Rate limiting (requests per day)
    FREE_TIER_LIMIT = 1000
    PRO_TIER_LIMIT = 1000  # Same as free - no premium tiers

    # Max rows per request
    MAX_ROWS_FREE = 100000
    MAX_ROWS_PRO = 100000  # Same as free - no premium tiers
