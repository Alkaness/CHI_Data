import unittest

from src.transform import transform_day_payload, transform_to_dataframe


class TransformTests(unittest.TestCase):
    def setUp(self):
        self.sample = {
            "daily": {
                "time": ["2025-08-01"],
                "temperature_2m_max": [25.0],
                "temperature_2m_min": [12.0],
                "sunrise": ["2025-08-01T03:50:00Z"],
                "sunset": ["2025-08-01T19:45:00Z"],
                "precipitation_hours": [5],
            }
        }

    def test_transform_day_payload_maps_expected_fields(self):
        result = transform_day_payload(self.sample)
        self.assertEqual(result["date"], "2025-08-01")
        self.assertAlmostEqual(result["temp_max_c"], 25.0)
        self.assertAlmostEqual(result["temp_min_c"], 12.0)
        self.assertAlmostEqual(result["temp_max_f"], 77.0)
        self.assertAlmostEqual(result["temp_min_f"], 53.6)
        self.assertEqual(result["precip_hours"], 5.0)

    def test_transform_to_dataframe_converts_timestamp_columns(self):
        frame = transform_to_dataframe(self.sample)
        self.assertEqual(frame.shape[0], 1)
        self.assertTrue(frame.loc[0, "sunrise"].tzinfo is not None)
        self.assertTrue(frame.loc[0, "sunset"].tzinfo is not None)


if __name__ == "__main__":
    unittest.main()
