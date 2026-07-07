"""Infer synthetic-data field schemas from real sample rows (e.g. from Kaggle).

This lets the engine "clone" a dataset's shape - column names, rough numeric
ranges, date ranges and categorical distributions - without ever storing or
replaying the real rows themselves; only the inferred schema is kept.
"""

import re
from collections import Counter
from datetime import datetime
from typing import Dict, List

from .schema import FieldSchema

_DATE_FORMATS = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S', '%m-%d-%Y']
_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

MAX_CATEGORY_VALUES = 25
SAMPLE_LIMIT = 200


def infer_schema(rows: List[Dict[str, str]], max_sample: int = 1000) -> List[FieldSchema]:
    """Infer a list of FieldSchema definitions that approximate the shape of `rows`."""
    if not rows:
        return []

    sample = rows[:max_sample]
    columns = list(sample[0].keys())

    return [
        _infer_field(column, [r.get(column, '') for r in sample if r.get(column)])
        for column in columns
    ]


def _infer_field(column: str, values: List[str]) -> FieldSchema:
    if not values:
        return FieldSchema(name=column, field_type='string', constraints={'min_length': 3, 'max_length': 20})

    probe = values[:SAMPLE_LIMIT]

    if all(_EMAIL_RE.match(v) for v in probe):
        return FieldSchema(name=column, field_type='email', constraints={})

    if _all_match(probe, _parse_int):
        nums = [_parse_int(v) for v in values]
        return FieldSchema(name=column, field_type='integer', constraints={'min': min(nums), 'max': max(nums)})

    if _all_match(probe, _parse_float):
        nums = [_parse_float(v) for v in values]
        return FieldSchema(name=column, field_type='float', constraints={
            'min': round(min(nums), 2), 'max': round(max(nums), 2), 'precision': 2,
        })

    date_format = _detect_date_format(probe)
    if date_format:
        parsed = [datetime.strptime(v, date_format) for v in values if _try_parse(v, date_format)]
        return FieldSchema(name=column, field_type='date', constraints={
            'start': min(parsed).strftime('%Y-%m-%d'),
            'end': max(parsed).strftime('%Y-%m-%d'),
        })

    unique_values = set(values)
    category_threshold = max(5, len(values) * 0.5)
    if len(unique_values) <= MAX_CATEGORY_VALUES and len(unique_values) <= category_threshold:
        counts = Counter(values)
        total = sum(counts.values())
        choices = list(counts.keys())
        weights = [counts[c] / total for c in choices]
        return FieldSchema(name=column, field_type='category', constraints={'choices': choices, 'weights': weights})

    lengths = [len(v) for v in values]
    return FieldSchema(name=column, field_type='string', constraints={
        'min_length': min(lengths), 'max_length': max(lengths),
    })


def _parse_int(value: str):
    return int(value)


def _parse_float(value: str):
    return float(value)


def _all_match(values: List[str], parser) -> bool:
    for value in values:
        try:
            parser(value)
        except (ValueError, TypeError):
            return False
    return True


def _try_parse(value: str, fmt: str):
    try:
        return datetime.strptime(value, fmt)
    except ValueError:
        return None


def _detect_date_format(values: List[str]):
    for fmt in _DATE_FORMATS:
        if all(_try_parse(v, fmt) for v in values):
            return fmt
    return None
