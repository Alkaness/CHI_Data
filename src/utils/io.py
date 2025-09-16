from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

import pandas as pd

from src.config import PipelineConfig


def ensure_dir(path: Path | str) -> Path:
    """Create ``path`` (including parents) and return it as a ``Path`` object."""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def ensure_raw_outpath(base_dir: Path | str, day_str: str) -> Path:
    """Return the file path for a raw JSON artefact, creating the day folder."""
    out_dir = ensure_dir(Path(base_dir) / day_str)
    return out_dir / "response.json"


def ensure_proc_outpath(base_dir: Path | str, day_str: str) -> Path:
    """Return the file path for a processed parquet artefact, creating the folder."""
    out_dir = ensure_dir(Path(base_dir) / day_str)
    return out_dir / "data.parquet"


def load_sql_file(
    config: PipelineConfig, filename: str, backend: str | None = None
) -> str:
    """Read a SQL file for the requested backend from the configured resource tree."""
    if backend == "sqlite":
        base_dir = config.sqlite_sql_dir
    elif backend == "postgres":
        base_dir = config.pg_sql_dir
    else:
        base_dir = config.sql_dir

    path = base_dir / filename
    return path.read_text(encoding="utf-8")


def json_default(value):
    """Serialize pandas-aware values for JSON dumps used throughout the project."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if pd.isna(value):
        return None
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def utc_isoformat(dt: datetime | None = None) -> str:
    """Format a datetime as an ISO-8601 string normalised to UTC."""
    dt = dt or datetime.now(UTC)
    return dt.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
