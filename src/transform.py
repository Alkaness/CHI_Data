from __future__ import annotations

from collections import OrderedDict
from typing import Any

import pandas as pd

from src.utils.schema import FIELD_MAP, KEEP_ORDER


def _c_to_f(celsius: float | None) -> float | None:
    """Convert Celsius to Fahrenheit, returning ``None`` when the input is missing."""
    return None if celsius is None else (celsius * 9.0 / 5.0 + 32.0)


def transform_day_payload(per_day_json: dict) -> OrderedDict[str, Any]:
    """Flatten the per-day section of the API response into a normalised mapping."""
    daily = per_day_json.get("daily", {})
    transformed: dict[str, Any] = {}
    if isinstance(daily.get("time"), list) and daily["time"]:
        transformed["date"] = daily["time"][0]

    for in_key, (out_key, cleaner) in FIELD_MAP.items():
        if in_key == "time":
            continue
        value = None
        values = daily.get(in_key)
        if isinstance(values, list) and values:
            value = values[0]
        transformed[out_key] = cleaner(value)

    transformed["temp_max_f"] = _c_to_f(transformed.get("temp_max_c"))
    transformed["temp_min_f"] = _c_to_f(transformed.get("temp_min_c"))

    ordered = OrderedDict((key, transformed.get(key)) for key in KEEP_ORDER)
    for key, value in transformed.items():
        if key not in ordered:
            ordered[key] = value
    return ordered


def transform_to_dataframe(per_day_json: dict) -> pd.DataFrame:
    """Return a single-row ``DataFrame`` built from :func:`transform_day_payload`."""
    cleaned = transform_day_payload(per_day_json)
    data_frame = pd.DataFrame([cleaned])
    for timestamp_column in ("sunrise", "sunset"):
        if data_frame[timestamp_column].notna().any():
            data_frame[timestamp_column] = pd.to_datetime(
                data_frame[timestamp_column], errors="coerce"
            )
    return data_frame
