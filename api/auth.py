"""API key authentication and usage tracking for the FastAPI layer."""

import os
import sqlite3
from dataclasses import dataclass
from datetime import date
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer_scheme = HTTPBearer(auto_error=False)

DEFAULT_DB = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'web',
    'syngen.db',
)
FREE_TIER_LIMIT = int(os.environ.get('FREE_TIER_LIMIT', '1000'))
MAX_ROWS = int(os.environ.get('MAX_ROWS_FREE', '100000'))


@dataclass
class ApiUser:
    id: int
    is_pro: bool
    requests_today: int
    last_request_date: Optional[str]


def _db_path() -> str:
    url = os.environ.get('DATABASE_URL', '')
    if url.startswith('sqlite:///'):
        return url.replace('sqlite:///', '', 1)
    return DEFAULT_DB


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def _lookup_user(api_key: str) -> Optional[sqlite3.Row]:
    with _get_connection() as conn:
        return conn.execute(
            'SELECT id, is_pro, requests_today, last_request_date, is_active '
            'FROM users WHERE api_key = ?',
            (api_key,),
        ).fetchone()


def _daily_limit(is_pro: bool) -> int:
    return FREE_TIER_LIMIT


def _max_rows(is_pro: bool) -> int:
    return MAX_ROWS


def _effective_requests_today(row: sqlite3.Row) -> int:
    today = date.today().isoformat()
    last = row['last_request_date']
    if last != today:
        return 0
    return row['requests_today'] or 0


def _try_consume_request(user_id: int, limit: int) -> bool:
    """Atomically increment usage only if the user is under their daily limit."""
    today = date.today().isoformat()
    with _get_connection() as conn:
        cursor = conn.execute(
            '''UPDATE users SET
                requests_today = CASE WHEN last_request_date = ? THEN requests_today + 1 ELSE 1 END,
                last_request_date = ?,
                total_requests = total_requests + 1
               WHERE id = ? AND is_active = 1
               AND (
                 last_request_date IS NULL OR last_request_date != ?
                 OR (last_request_date = ? AND requests_today < ?)
               )''',
            (today, today, user_id, today, today, limit),
        )
        conn.commit()
        return cursor.rowcount > 0


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> ApiUser:
    if not credentials or credentials.scheme.lower() != 'bearer':
        raise HTTPException(
            status_code=401,
            detail='Missing or invalid Authorization header. Use: Bearer YOUR_API_KEY',
        )

    row = _lookup_user(credentials.credentials)
    if not row or not row['is_active']:
        raise HTTPException(status_code=401, detail='Invalid or inactive API key')

    return ApiUser(
        id=row['id'],
        is_pro=bool(row['is_pro']),
        requests_today=_effective_requests_today(row),
        last_request_date=row['last_request_date'],
    )


def consume_request_quota(user: ApiUser = Depends(get_current_user)) -> ApiUser:
    """Authenticate and atomically consume one request from the user's daily quota."""
    limit = _daily_limit(user.is_pro)
    if not _try_consume_request(user.id, limit):
        raise HTTPException(
            status_code=429,
            detail=f'Daily limit of {limit} requests reached. Resets at midnight UTC.',
        )
    return user


def enforce_row_limit(rows: int, user: ApiUser) -> None:
    max_rows = _max_rows(user.is_pro)
    if rows > max_rows:
        raise HTTPException(
            status_code=400,
            detail=f'Maximum {max_rows:,} rows allowed per request.',
        )
