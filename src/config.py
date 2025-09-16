from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env_float(name: str, default: float) -> float:
    """Return a float from an environment variable or fall back to ``default``."""
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} must be a float") from exc


def _env_int(name: str, default: int) -> int:
    """Return an integer from an environment variable or fall back to ``default``."""
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} must be an integer") from exc


def _env_str(name: str, default: str) -> str:
    """Return a non-empty string from the environment or the provided default."""
    raw = os.getenv(name)
    return raw if raw is not None and raw.strip() else default


@dataclass(frozen=True)
class PipelineConfig:
    """Configuration container materialised from environment variables."""

    latitude: float
    longitude: float
    start_date: str
    end_date: str
    timezone: str
    db_backend: str
    db_url: str
    fetch_batch_days: int | None
    project_root: Path
    data_root: Path
    resources_root: Path
    raw_root: Path
    proc_root: Path
    reports_root: Path
    db_root: Path
    sqlite_root: Path
    pg_root: Path
    db_path: Path
    sql_dir: Path
    sqlite_sql_dir: Path
    pg_sql_dir: Path
    schema_sqlite: Path
    schema_postgres: Path

    @classmethod
    def from_env(cls) -> "PipelineConfig":
        """Construct a :class:`PipelineConfig` using project-relative defaults."""
        script_dir = Path(__file__).resolve().parent
        project_root = script_dir.parent
        data_root = project_root / "data"
        resources_root = project_root / "resources"
        db_root = project_root / "db"
        sqlite_root = db_root / "sqlite"
        pg_root = db_root / "pg"

        fetch_days_raw = _env_int("PIPELINE_FETCH_BATCH_DAYS", 30)
        fetch_batch_days = fetch_days_raw if fetch_days_raw > 0 else None

        db_backend = _env_str("PIPELINE_DB_BACKEND", "sqlite").lower()
        if db_backend not in {"sqlite", "postgres"}:
            raise ValueError(
                "PIPELINE_DB_BACKEND must be either 'sqlite' or 'postgres'"
            )

        return cls(
            latitude=_env_float("PIPELINE_LATITUDE", 50.45),
            longitude=_env_float("PIPELINE_LONGITUDE", 30.52),
            start_date=_env_str("PIPELINE_START_DATE", "2025-08-01"),
            end_date=_env_str("PIPELINE_END_DATE", "2025-09-13"),
            timezone=_env_str("PIPELINE_TIMEZONE", "Europe/Kyiv"),
            db_backend=db_backend,
            db_url=_env_str("PIPELINE_DB_URL", "").strip(),
            fetch_batch_days=fetch_batch_days,
            project_root=project_root,
            data_root=data_root,
            resources_root=resources_root,
            raw_root=data_root / "raw",
            proc_root=data_root / "processed",
            reports_root=data_root / "reports",
            db_root=db_root,
            sqlite_root=sqlite_root,
            pg_root=pg_root,
            db_path=sqlite_root / "weather.db",
            sql_dir=resources_root / "sql",
            sqlite_sql_dir=resources_root / "sql" / "sqlite",
            pg_sql_dir=resources_root / "sql" / "pg",
            schema_sqlite=resources_root / "sql" / "sqlite" / "init.sql",
            schema_postgres=resources_root / "sql" / "pg" / "init.sql",
        )


ALL_DAILY_VARS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "apparent_temperature_max",
    "apparent_temperature_min",
    "precipitation_sum",
    "rain_sum",
    "showers_sum",
    "snowfall_sum",
    "precipitation_hours",
    "sunrise",
    "sunset",
    "daylight_duration",
    "sunshine_duration",
    "shortwave_radiation_sum",
    "windspeed_10m_max",
    "windgusts_10m_max",
    "winddirection_10m_dominant",
    "weathercode",
    "et0_fao_evapotranspiration",
    "uv_index_max",
    "uv_index_clear_sky_max",
]


METRIC_SQL_FILES = [
    "metrics_rolling_7d.sql",
    "metrics_heatwave_streaks.sql",
    "metrics_sunshine_vs_temp.sql",
]
