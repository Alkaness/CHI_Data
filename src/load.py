from __future__ import annotations

import json
import logging
import os

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from src.config import PipelineConfig, _env_int, _env_str
from src.transform import transform_to_dataframe
from src.utils.io import (
    ensure_dir,
    ensure_proc_outpath,
    ensure_raw_outpath,
    load_sql_file,
    utc_isoformat,
)

logger = logging.getLogger(__name__)


def get_db_engine(config: PipelineConfig):
    """Return a SQLAlchemy engine for the configured backend."""
    if config.db_backend == "sqlite":
        ensure_dir(config.db_path.parent)
        return create_engine(f"sqlite:///{config.db_path}", future=True)

    if config.db_backend == "postgres":
        if config.db_url:
            return create_engine(config.db_url, future=True)

        host = _env_str("POSTGRES_HOST", "localhost")
        port = _env_int("POSTGRES_PORT", 5432)
        database = _env_str("POSTGRES_DB", "weather")
        user = _env_str("POSTGRES_USER", "weather")
        password = os.getenv("POSTGRES_PASSWORD")

        url = URL.create(
            "postgresql+psycopg2",
            username=user or None,
            password=password or None,
            host=host,
            port=port,
            database=database,
        )
        return create_engine(url, future=True)

    raise ValueError(f"Unsupported database backend: {config.db_backend}")


def ensure_db_and_table(config: PipelineConfig, engine=None):
    """Create the database (if needed) and ensure the weather table exists."""
    engine = engine or get_db_engine(config)
    schema_path = (
        config.schema_sqlite
        if config.db_backend == "sqlite"
        else config.schema_postgres
    )
    schema_text = schema_path.read_text(encoding="utf-8")

    with engine.begin() as conn:
        raw = conn.connection
        dbapi_conn = getattr(raw, "driver_connection", raw)
        if config.db_backend == "sqlite":
            dbapi_conn.executescript(schema_text)
        else:
            with dbapi_conn.cursor() as cursor:
                cursor.execute(schema_text)

    return engine


def load_upsert_statement(config: PipelineConfig):
    """Load the parametrised UPSERT statement for the ``weather_daily`` table."""
    return text(load_sql_file(config, "upsert_weather_daily.sql"))


def df_rows_for_upsert(data_frame: pd.DataFrame):
    """Yield serialisable mappings for the provided single-row ``DataFrame``."""
    record = data_frame.iloc[0].to_dict()

    record["date"] = (
        pd.to_datetime(record.get("date"), errors="coerce").date().isoformat()
        if record.get("date")
        else None
    )

    for ts_col in ("sunrise", "sunset"):
        value = record.get(ts_col)
        if pd.isna(value):
            record[ts_col] = None
        elif hasattr(value, "isoformat"):
            record[ts_col] = value.isoformat()
        else:
            record[ts_col] = str(value)

    numeric_columns = [
        "temp_max_c",
        "temp_min_c",
        "temp_max_f",
        "temp_min_f",
        "app_temp_max_c",
        "app_temp_min_c",
        "precip_mm",
        "rain_mm",
        "showers_mm",
        "snowfall_mm",
        "precip_hours",
        "daylight_sec",
        "sunshine_sec",
        "shortwave_radiation_mj_m2",
        "wind_max_kmh",
        "wind_gust_max_kmh",
        "wind_dir_deg",
        "weather_code",
        "et0_mm",
        "uv_index_max",
        "uv_index_clear_sky_max",
    ]
    for column in numeric_columns:
        value = record.get(column)
        if pd.isna(value):
            record[column] = None
            continue
        if column == "weather_code":
            record[column] = int(value)
        else:
            record[column] = float(value)

    record["source"] = "open-meteo"
    record["ingested_at"] = utc_isoformat()
    yield record


def split_save_and_upsert(
    full_json: dict,
    config: PipelineConfig,
    *,
    engine=None,
    upsert_stmt=None,
) -> None:
    """Persist artefacts and upsert each day present within the API batch payload."""
    if engine is None:
        engine = get_db_engine(config)
    if upsert_stmt is None:
        upsert_stmt = load_upsert_statement(config)

    daily = (full_json or {}).get("daily")
    if not daily or "time" not in daily:
        raise RuntimeError("Response missing 'daily.time' to split by day")

    day_identifiers = daily["time"]
    total_days = len(day_identifiers)

    with engine.begin() as conn:
        for index, day in enumerate(day_identifiers):
            per_day = {
                **{
                    key: value
                    for key, value in full_json.items()
                    if key
                    not in (
                        "daily",
                        "hourly",
                        "current",
                        "_requested_daily",
                        "_accepted_daily",
                        "_dropped_daily",
                    )
                },
                "daily": {},
                "_requested_daily": full_json.get("_requested_daily", []),
                "_accepted_daily": full_json.get("_accepted_daily", []),
                "_dropped_daily": full_json.get("_dropped_daily", []),
            }
            for variable, values in daily.items():
                if variable == "time":
                    per_day["daily"]["time"] = [day]
                    continue
                if isinstance(values, list) and len(values) == total_days:
                    per_day["daily"][variable] = [values[index]]
                else:
                    per_day["daily"][variable] = [None]

            raw_path = ensure_raw_outpath(config.raw_root, day)
            with raw_path.open("w", encoding="utf-8") as handle:
                json.dump(per_day, handle, ensure_ascii=False, indent=2)
            logger.info("Saved raw: %s", raw_path)

            data_frame = transform_to_dataframe(per_day)

            proc_path = ensure_proc_outpath(config.proc_root, day)
            data_frame.to_parquet(proc_path, index=False, engine="pyarrow")
            logger.info("Saved processed: %s", proc_path)

            upsert_params = list(df_rows_for_upsert(data_frame))
            conn.execute(upsert_stmt, upsert_params)
            logger.info("Upserted into database for %s", day)
