"""Minimal client for the Kaggle public API (dataset search + download).

Credentials are taken per-call (username + API key from the caller's Kaggle
account settings, https://www.kaggle.com/settings -> API -> Create New Token)
and used only for that request's HTTP basic auth - nothing is persisted here.
"""

import csv
import io
import zipfile
from typing import Any, Dict, List

import requests

KAGGLE_API_BASE = "https://www.kaggle.com/api/v1"
REQUEST_TIMEOUT = 30
DOWNLOAD_TIMEOUT = 120


class KaggleError(Exception):
    """Raised for any Kaggle API failure (auth, not found, network, ...)."""


class KaggleClient:
    """Thin wrapper around the Kaggle REST API for searching and downloading datasets."""

    def __init__(self, username: str, key: str):
        if not username or not key:
            raise KaggleError("Kaggle username and API key are required")
        self._auth = (username, key)

    def search_datasets(self, query: str, page: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
        """Search public datasets by keyword."""
        response = requests.get(
            f"{KAGGLE_API_BASE}/datasets/list",
            params={"search": query, "page": page, "pageSize": page_size},
            auth=self._auth,
            timeout=REQUEST_TIMEOUT,
        )
        self._raise_for_status(response)
        return response.json()

    def fetch_dataset_rows(self, owner: str, dataset: str, max_rows: int = 2000) -> List[Dict[str, str]]:
        """Download a dataset and return rows from the first CSV file it contains."""
        response = requests.get(
            f"{KAGGLE_API_BASE}/datasets/download/{owner}/{dataset}",
            auth=self._auth,
            timeout=DOWNLOAD_TIMEOUT,
        )
        self._raise_for_status(response)

        try:
            archive = zipfile.ZipFile(io.BytesIO(response.content))
        except zipfile.BadZipFile as exc:
            raise KaggleError("Downloaded dataset is not a valid zip archive") from exc

        csv_names = sorted(n for n in archive.namelist() if n.lower().endswith('.csv'))
        if not csv_names:
            raise KaggleError(f"No CSV files found in dataset {owner}/{dataset}")

        with archive.open(csv_names[0]) as raw_file:
            text_stream = io.TextIOWrapper(raw_file, encoding='utf-8', errors='replace')
            reader = csv.DictReader(text_stream)
            rows = []
            for row in reader:
                if len(rows) >= max_rows:
                    break
                rows.append(row)
            return rows

    @staticmethod
    def _raise_for_status(response: requests.Response) -> None:
        if response.status_code in (401, 403):
            raise KaggleError("Kaggle rejected these credentials - check your username and API key")
        if response.status_code == 404:
            raise KaggleError("Dataset not found")
        if not response.ok:
            raise KaggleError(f"Kaggle API error ({response.status_code}): {response.text[:200]}")
