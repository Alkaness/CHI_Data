#!/usr/bin/env python3

import argparse
import logging
import sys
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

if __package__ is None or __package__ == "":  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from sqlalchemy import inspect, text

from src.config import PipelineConfig
from src.load import get_db_engine

logger = logging.getLogger(__name__)


def _timestamped_filename(suffix: str) -> str:
    """Return an ISO-like filename for the exported dataset."""
    now = datetime.now(UTC)
    return f"weather_daily_{now.strftime('%Y%m%d_%H%M%S')}.{suffix}"


def dump_table(config: PipelineConfig, output_root: Path) -> Path:
    """Dump the ``weather_daily`` table to a CSV file and return the path."""
    engine = get_db_engine(config)
    inspector = inspect(engine)
    if not inspector.has_table("weather_daily"):
        raise RuntimeError(
            "Table 'weather_daily' does not exist in the configured database"
        )

    out_dir = output_root / ("sqlite" if config.db_backend == "sqlite" else "pg")
    out_dir.mkdir(parents=True, exist_ok=True)

    dump_path = out_dir / _timestamped_filename("csv")

    with engine.connect() as conn:
        data_frame = pd.read_sql(
            text("SELECT * FROM weather_daily ORDER BY date"), conn
        )

    data_frame.to_csv(dump_path, index=False)
    return dump_path


def main() -> None:
    """CLI entry point for creating weather table exports."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(
        description="Dump weather_daily table to CSV in db/sqlite or db/pg"
    )
    config = PipelineConfig.from_env()

    parser.add_argument(
        "--output-root",
        type=Path,
        default=config.db_root,
        help="Directory that will contain pg/ or sqlite/ dump folders",
    )
    parser.add_argument(
        "--backend",
        choices=("sqlite", "postgres"),
        help="Override backend (defaults to env-configured backend)",
    )

    args = parser.parse_args()
    backend = (args.backend or config.db_backend).lower()
    if backend not in {"sqlite", "postgres"}:
        raise ValueError(f"Unsupported backend for dump: {backend}")

    if backend != config.db_backend:
        config = replace(config, db_backend=backend)

    dump_path = dump_table(config, args.output_root)
    logger.info("Exported weather_daily to %s", dump_path)


if __name__ == "__main__":
    main()
