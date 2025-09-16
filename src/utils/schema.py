from __future__ import annotations

from typing import Callable


def clip_num(
    value, lo: float | None = None, hi: float | None = None, *, none_if_out: bool = True
):
    """Clamp numeric inputs, returning ``None`` for invalid/out-of-range values."""
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if lo is not None and numeric < lo:
        return None if none_if_out else lo
    if hi is not None and numeric > hi:
        return None if none_if_out else hi
    return numeric


FIELD_MAP: dict[str, tuple[str, Callable[[object], object]]] = {
    "time": ("date", lambda s: s),
    "temperature_2m_max": ("temp_max_c", lambda v: clip_num(v, -100, 70)),
    "temperature_2m_min": ("temp_min_c", lambda v: clip_num(v, -120, 70)),
    "apparent_temperature_max": ("app_temp_max_c", lambda v: clip_num(v, -120, 80)),
    "apparent_temperature_min": ("app_temp_min_c", lambda v: clip_num(v, -120, 80)),
    "precipitation_sum": ("precip_mm", lambda v: clip_num(v, 0, None)),
    "rain_sum": ("rain_mm", lambda v: clip_num(v, 0, None)),
    "showers_sum": ("showers_mm", lambda v: clip_num(v, 0, None)),
    "snowfall_sum": ("snowfall_mm", lambda v: clip_num(v, 0, None)),
    "precipitation_hours": ("precip_hours", lambda v: clip_num(v, 0, 24)),
    "sunrise": ("sunrise", lambda s: s),
    "sunset": ("sunset", lambda s: s),
    "daylight_duration": ("daylight_sec", lambda v: clip_num(v, 0, 86400)),
    "sunshine_duration": ("sunshine_sec", lambda v: clip_num(v, 0, 86400)),
    "shortwave_radiation_sum": (
        "shortwave_radiation_mj_m2",
        lambda v: clip_num(v, 0, None),
    ),
    "windspeed_10m_max": ("wind_max_kmh", lambda v: clip_num(v, 0, 300)),
    "windgusts_10m_max": ("wind_gust_max_kmh", lambda v: clip_num(v, 0, 400)),
    "winddirection_10m_dominant": ("wind_dir_deg", lambda v: clip_num(v, 0, 360)),
    "weathercode": ("weather_code", lambda v: clip_num(v, 0, 99)),
    "et0_fao_evapotranspiration": ("et0_mm", lambda v: clip_num(v, 0, None)),
    "uv_index_max": ("uv_index_max", lambda v: clip_num(v, 0, 25)),
    "uv_index_clear_sky_max": (
        "uv_index_clear_sky_max",
        lambda v: clip_num(v, 0, 25),
    ),
}


KEEP_ORDER = [
    "date",
    "temp_max_c",
    "temp_min_c",
    "temp_max_f",
    "temp_min_f",
    "app_temp_max_c",
    "app_temp_min_c",
    "precip_mm",
    "rain_mm",
    "showers_mm",
    "snowfall_mm",
    "precip_hours",
    "sunrise",
    "sunset",
    "daylight_sec",
    "sunshine_sec",
    "shortwave_radiation_mj_m2",
    "wind_max_kmh",
    "wind_gust_max_kmh",
    "wind_dir_deg",
    "weather_code",
    "et0_mm",
    "uv_index_max",
    "uv_index_clear_sky_max",
]
