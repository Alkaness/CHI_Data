from __future__ import annotations

import json
import logging
import re
from datetime import date, timedelta
from itertools import chain
from typing import Iterator

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RetryError
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


def http_get_with_retries(
    url: str, params: dict, max_attempts: int = 5, timeout: int = 60
):
    """Perform an HTTP GET with retry/backoff semantics."""
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    retry = Retry(
        total=max_attempts - 1,
        connect=max_attempts - 1,
        read=max_attempts - 1,
        status=max_attempts - 1,
        allowed_methods=("GET",),
        status_forcelist=(429, 500, 502, 503, 504),
        backoff_factor=1,
        respect_retry_after_header=True,
        raise_on_status=False,
    )

    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    try:
        return session.get(url, params=params, timeout=timeout)
    except RetryError as exc:
        raise RuntimeError("Exhausted retries for HTTP GET") from exc
    finally:
        session.close()


def parse_unknown_daily_vars(error_text: str) -> set[str]:
    """Extract unsupported variable names from an API error payload."""
    unsupported: set[str] = set()
    patterns = [
        r"[\"']([a-z0-9_]+)[\"']\s+is not a known variable",
        r"Invalid value for parameter 'daily'[:\s]+([a-z0-9_,\s-]+)",
        r"Unknown daily variables?[:\s]+([a-z0-9_,\s-]+)",
        r"Unsupported daily variables?[:\s]+([a-z0-9_,\s-]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, error_text, flags=re.IGNORECASE)
        if not match:
            continue
        group = match.group(1)
        for token in re.split(r"[,\s]+", group.strip()):
            token = token.strip().lower()
            if token and re.fullmatch(r"[a-z0-9_]+", token):
                unsupported.add(token)
    return unsupported


def _iter_date_chunks(start_date: str, end_date: str, chunk_days: int | None):
    """Yield inclusive date ranges, optionally splitting them into ``chunk_days`` blocks."""
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    if chunk_days is None:
        yield start.isoformat(), end.isoformat()
        return

    if chunk_days < 1:
        chunk_days = 1

    current = start
    while current <= end:
        chunk_end = min(current + timedelta(days=chunk_days - 1), end)
        yield current.isoformat(), chunk_end.isoformat()
        current = chunk_end + timedelta(days=1)


def fetch_daily_archive(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    timezone: str,
    daily_vars,
    *,
    batch_days: int | None,
):
    """Stream Open-Meteo archive payloads for the given co-ordinates and dates."""
    remaining_variables = list(daily_vars)
    removed_all: set[str] = set()
    requested_daily = list(daily_vars)
    accepted_daily: list[str] | None = None

    def chunk_generator() -> Iterator[dict]:
        nonlocal remaining_variables, removed_all, accepted_daily
        for chunk_start, chunk_end in _iter_date_chunks(
            start_date, end_date, batch_days
        ):
            logger.info("Fetching archive chunk %s to %s", chunk_start, chunk_end)
            while True:
                params = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "start_date": chunk_start,
                    "end_date": chunk_end,
                    "timezone": timezone,
                    "daily": ",".join(remaining_variables),
                }
                response = http_get_with_retries(OPEN_METEO_ARCHIVE_URL, params=params)
                if response.status_code == 200:
                    accepted_daily = list(remaining_variables)
                    response_data = response.json()
                    response_data["_requested_daily"] = requested_daily
                    response_data["_accepted_daily"] = accepted_daily
                    response_data["_dropped_daily"] = sorted(removed_all)
                    yield response_data
                    break

                if response.status_code == 400:
                    try:
                        payload = response.json()
                        err_text = json.dumps(payload)
                    except Exception:
                        err_text = response.text or ""
                    unknown = parse_unknown_daily_vars(err_text)
                    if not unknown:
                        raise RuntimeError(
                            f"Open-Meteo 400 error: {err_text or 'Bad Request'}"
                        )
                    remaining_variables = [
                        variable
                        for variable in remaining_variables
                        if variable not in unknown
                    ]
                    removed_all.update(unknown)
                    if not remaining_variables:
                        raise RuntimeError(
                            f"All daily variables were rejected by the API. Error: {err_text}"
                        )
                    continue

                try:
                    response_message = response.json()
                except Exception:
                    response_message = response.text
                raise RuntimeError(
                    f"Open-Meteo error {response.status_code}: {response_message}"
                )

    chunk_iterator = chunk_generator()
    try:
        first_chunk = next(chunk_iterator)
    except StopIteration as exc:
        raise RuntimeError("No data returned for the requested date range") from exc

    metadata = {
        "_requested_daily": requested_daily,
        "_accepted_daily": accepted_daily or remaining_variables,
        "_dropped_daily": sorted(removed_all),
    }

    return metadata, chain([first_chunk], chunk_iterator)
