from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from src.config import PipelineConfig
from src.load import get_db_engine
from src.utils.io import ensure_dir, json_default, load_sql_file, utc_isoformat

logger = logging.getLogger(__name__)


def calculate_metrics(
    config: PipelineConfig,
    query_files: list[str],
    *,
    engine=None,
):
    """Execute SQL files, capture their results, and materialise report artefacts."""
    engine = engine or get_db_engine(config)

    datasets = []
    with engine.begin() as conn:
        for filename in query_files:
            sql = load_sql_file(config, filename, backend=config.db_backend)
            name = Path(filename).stem
            datasets.append((name, pd.read_sql_query(sql, conn)))

    generated_at = datetime.now(UTC)
    reports_dir = ensure_dir(
        config.reports_root / generated_at.strftime("%Y%m%d_%H%M%S")
    )

    manifest = {
        "generated_utc": utc_isoformat(generated_at),
        "metrics": [],
    }

    for name, frame in datasets:
        json_path = reports_dir / f"{name}.json"
        with json_path.open("w", encoding="utf-8") as handle:
            json.dump(
                frame.to_dict(orient="records"),
                handle,
                ensure_ascii=False,
                indent=2,
                default=json_default,
            )
        logger.info("Wrote %s", json_path)

        csv_path = reports_dir / f"{name}.csv"
        frame.to_csv(csv_path, index=False)
        logger.info("Wrote %s", csv_path)

        manifest["metrics"].append(
            {
                "name": name,
                "rows": len(frame),
                "json": json_path.name,
                "csv": csv_path.name,
            }
        )

    meta_path = reports_dir / "metadata.json"
    with meta_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2, default=json_default)
    logger.info("Wrote %s", meta_path)
