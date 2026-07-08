"""Symmetric encryption for secrets we store on a user's behalf (e.g. a saved Kaggle API key).

Keyed by APP_ENCRYPTION_KEY, an environment variable that must never be
committed to source control. This is deliberately a separate key from
Flask's SECRET_KEY (used to sign sessions) so that a session-related leak
doesn't also expose stored third-party credentials.
"""

import base64
import hashlib
import os
import sys

from cryptography.fernet import Fernet, InvalidToken

_IS_PRODUCTION = os.environ.get('FLASK_ENV') == 'production' or os.environ.get('PRODUCTION') == '1'


def _load_key() -> bytes:
    from config import Config

    raw = Config.APP_ENCRYPTION_KEY
    if raw:
        return raw.encode() if isinstance(raw, str) else raw

    if _IS_PRODUCTION:
        print('FATAL: APP_ENCRYPTION_KEY must be set in production.', file=sys.stderr)
        sys.exit(1)

    # Dev-only fallback so the app still runs out of the box.
    digest = hashlib.sha256(f"dev-only:{Config.SECRET_KEY}".encode()).digest()
    return base64.urlsafe_b64encode(digest)


_fernet = Fernet(_load_key())


def encrypt_secret(plaintext: str) -> str:
    """Encrypt a secret for storage; returns a string safe to put in a DB column."""
    return _fernet.encrypt(plaintext.encode()).decode()


def decrypt_secret(ciphertext: str) -> str:
    """Decrypt a value previously produced by encrypt_secret."""
    try:
        return _fernet.decrypt(ciphertext.encode()).decode()
    except InvalidToken as exc:
        raise ValueError("Stored secret could not be decrypted - APP_ENCRYPTION_KEY may have changed") from exc
