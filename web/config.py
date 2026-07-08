import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    # Encrypts secrets stored on a user's behalf (e.g. saved Kaggle API keys).
    # Set this explicitly in production: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    APP_ENCRYPTION_KEY = os.environ.get('APP_ENCRYPTION_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'syngen.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # App settings
    APP_NAME = 'SynGen Pro'
    APP_DESCRIPTION = 'Professional Synthetic Data Generation Service'

    # Rate limiting (requests per day)
    FREE_TIER_LIMIT = 1000
    PRO_TIER_LIMIT = 1000  # Same as free - no premium tiers

    # Max rows per request
    MAX_ROWS_FREE = 100000
    MAX_ROWS_PRO = 100000  # Same as free - no premium tiers
