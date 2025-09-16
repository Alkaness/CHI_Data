import os
import unittest
from pathlib import Path

from src.config import METRIC_SQL_FILES, PipelineConfig


class PipelineConfigTests(unittest.TestCase):
    ENV_KEYS = {
        "PIPELINE_FETCH_BATCH_DAYS",
        "PIPELINE_DB_BACKEND",
        "PIPELINE_DB_URL",
    }

    def setUp(self):
        self._original_env = {key: os.environ.get(key) for key in self.ENV_KEYS}
        for key in self.ENV_KEYS:
            os.environ.pop(key, None)

    def tearDown(self):
        for key, value in self._original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_defaults_use_project_structure(self):
        config = PipelineConfig.from_env()
        project_root = Path(__file__).resolve().parent.parent

        self.assertEqual(config.project_root, project_root)
        self.assertEqual(config.db_root, project_root / "db")
        self.assertEqual(config.sqlite_root, project_root / "db" / "sqlite")
        self.assertEqual(config.db_path, project_root / "db" / "sqlite" / "weather.db")
        self.assertEqual(config.fetch_batch_days, 30)

    def test_env_overrides_lowercase_backend_and_batch_none(self):
        os.environ["PIPELINE_FETCH_BATCH_DAYS"] = "0"
        os.environ["PIPELINE_DB_BACKEND"] = "POSTGRES"
        os.environ["PIPELINE_DB_URL"] = "postgresql://example"

        config = PipelineConfig.from_env()

        self.assertIsNone(config.fetch_batch_days)
        self.assertEqual(config.db_backend, "postgres")
        self.assertEqual(config.db_url, "postgresql://example")

    def test_metric_sql_files_defined(self):
        self.assertGreater(len(METRIC_SQL_FILES), 0)
        for name in METRIC_SQL_FILES:
            self.assertTrue(name.endswith(".sql"))


if __name__ == "__main__":
    unittest.main()
