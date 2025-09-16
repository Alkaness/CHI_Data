import json
import sqlite3
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from src.analytics import calculate_metrics
from src.config import METRIC_SQL_FILES, PipelineConfig


class AnalyticsTests(unittest.TestCase):
    def test_calculate_metrics_runs_queries_and_writes_reports(self):
        config = PipelineConfig.from_env()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            db_path = tmp / "weather.db"
            reports_root = tmp / "reports"
            sql_dir = tmp / "sql"
            sql_dir.mkdir()

            # Create simple SQL query file for testing
            query_name = "test_metric.sql"
            (sql_dir / query_name).write_text("SELECT 42 AS answer", encoding="utf-8")

            # Prepare empty SQLite database
            sqlite3.connect(db_path).close()

            test_config = replace(
                config,
                db_backend="sqlite",
                db_root=tmp,
                sqlite_root=tmp,
                pg_root=tmp,
                db_path=db_path,
                reports_root=reports_root,
                sql_dir=sql_dir,
                sqlite_sql_dir=sql_dir,
            )

            calculate_metrics(test_config, [query_name])

            subdirs = list(reports_root.iterdir())
            self.assertEqual(len(subdirs), 1)
            report_dir = subdirs[0]

            manifest = json.loads((report_dir / "metadata.json").read_text("utf-8"))
            self.assertEqual(manifest["metrics"][0]["name"], "test_metric")
            self.assertTrue((report_dir / "test_metric.json").exists())
            self.assertTrue((report_dir / "test_metric.csv").exists())


if __name__ == "__main__":
    unittest.main()
