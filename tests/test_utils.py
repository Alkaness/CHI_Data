import math
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.utils.io import (
    ensure_proc_outpath,
    ensure_raw_outpath,
    json_default,
    utc_isoformat,
)
from src.utils.schema import clip_num


class UtilsTests(unittest.TestCase):
    def test_ensure_outpaths_create_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw_path = ensure_raw_outpath(tmp, "2025-08-01")
            proc_path = ensure_proc_outpath(tmp, "2025-08-01")
            self.assertTrue(raw_path.parent.exists())
            self.assertTrue(proc_path.parent.exists())
            self.assertTrue(str(raw_path).endswith("response.json"))
            self.assertTrue(str(proc_path).endswith("data.parquet"))

    def test_json_default_handles_datetime_and_nan(self):
        iso = json_default(pd.Timestamp("2025-01-01T00:00:00Z"))
        self.assertEqual(iso, "2025-01-01T00:00:00+00:00")
        self.assertIsNone(json_default(math.nan))
        with self.assertRaises(TypeError):
            json_default(object())

    def test_utc_isoformat_appends_z(self):
        value = utc_isoformat()
        self.assertTrue(value.endswith("Z"))

    def test_clip_num_bounds(self):
        self.assertEqual(clip_num(5, lo=0, hi=10), 5)
        self.assertIsNone(clip_num(-5, lo=0, hi=10))
        self.assertEqual(clip_num(-5, lo=0, hi=10, none_if_out=False), 0)
        self.assertIsNone(clip_num("not-a-number"))


if __name__ == "__main__":
    unittest.main()
