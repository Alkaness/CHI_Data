#!/usr/bin/env python3


import logging
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.analytics import calculate_metrics
from src.config import ALL_DAILY_VARS, METRIC_SQL_FILES, PipelineConfig
from src.extract import fetch_daily_archive
from src.load import ensure_db_and_table, load_upsert_statement, split_save_and_upsert
from src.utils.logging import setup_logging

logger = logging.getLogger(__name__)


def run() -> None:
    """Execute the end-to-end pipeline from data extraction to analytics."""
    setup_logging()
    config = PipelineConfig.from_env()

    metadata, batch_iterator = fetch_daily_archive(
        latitude=config.latitude,
        longitude=config.longitude,
        start_date=config.start_date,
        end_date=config.end_date,
        timezone=config.timezone,
        daily_vars=ALL_DAILY_VARS,
        batch_days=config.fetch_batch_days,
    )
    dropped_variables = metadata.get("_dropped_daily", [])
    if dropped_variables:
        logger.info("Dropped unsupported daily vars: %s", ", ".join(dropped_variables))
    logger.info(
        "Accepted daily vars: %s",
        ", ".join(metadata.get("_accepted_daily", [])),
    )

    engine = ensure_db_and_table(config)
    upsert_statement = load_upsert_statement(config)
    for batch in batch_iterator:
        split_save_and_upsert(
            batch, config, engine=engine, upsert_stmt=upsert_statement
        )

    calculate_metrics(config, METRIC_SQL_FILES, engine=engine)


def main() -> None:
    """Entry point used when invoking the module as a script."""
    run()


if __name__ == "__main__":
    main()
