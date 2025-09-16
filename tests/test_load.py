import unittest

import pandas as pd

from src.load import df_rows_for_upsert


class LoadHelpersTests(unittest.TestCase):
    def test_df_rows_for_upsert_normalizes_values(self):
        df = pd.DataFrame(
            [
                {
                    "date": "2025-08-01",
                    "sunrise": pd.Timestamp("2025-08-01T03:45:00Z"),
                    "sunset": pd.Timestamp("2025-08-01T20:15:00Z"),
                    "temp_max_c": 25.0,
                    "temp_min_c": 12.0,
                    "temp_max_f": 77.0,
                    "temp_min_f": 53.6,
                    "weather_code": 3.0,
                    "precip_hours": float("nan"),
                }
            ]
        )

        record = next(df_rows_for_upsert(df))
        self.assertEqual(record["date"], "2025-08-01")
        self.assertEqual(record["temp_max_c"], 25.0)
        self.assertEqual(record["temp_min_f"], 53.6)
        self.assertEqual(record["weather_code"], 3)
        self.assertIsNone(record["precip_hours"])
        self.assertTrue(record["sunrise"].endswith("+00:00"))
        self.assertTrue(record["sunset"].endswith("+00:00"))
        self.assertEqual(record["source"], "open-meteo")
        self.assertTrue(record["ingested_at"].endswith("Z"))


if __name__ == "__main__":
    unittest.main()
