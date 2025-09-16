import unittest

from src.extract import _iter_date_chunks, parse_unknown_daily_vars


class ExtractHelpersTests(unittest.TestCase):
    def test_iter_date_chunks_without_chunking(self):
        chunks = list(_iter_date_chunks("2025-01-01", "2025-01-10", None))
        self.assertEqual(chunks, [("2025-01-01", "2025-01-10")])

    def test_iter_date_chunks_with_chunking(self):
        chunks = list(_iter_date_chunks("2025-01-01", "2025-01-10", 3))
        self.assertEqual(
            chunks,
            [
                ("2025-01-01", "2025-01-03"),
                ("2025-01-04", "2025-01-06"),
                ("2025-01-07", "2025-01-09"),
                ("2025-01-10", "2025-01-10"),
            ],
        )

    def test_parse_unknown_daily_vars_collects_tokens(self):
        payload = "Invalid value for parameter 'daily': foo_bar, TEMP_max, invalid-var"
        result = parse_unknown_daily_vars(payload)
        self.assertEqual(result, {"foo_bar", "temp_max"})


if __name__ == "__main__":
    unittest.main()
