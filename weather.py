#!/usr/bin/env python3
"""
Fetch Open-Meteo daily historical weather, save one raw JSON per day,
transform to a single-row DataFrame per day, save Parquet, and
UPSERT into SQLite **from memory** (no re-reading from Parquet).

Raw JSON:       ./data/YYYY-MM-DD/response.json
Processed PQ:    ./data/processed/YYYY-MM-DD/data.parquet
SQLite DB:       ./data/weather.db (created via schema.sql)
Table:           weather_daily
"""

import json
import os
import re
import time
from datetime import datetime
import requests
import pandas as pd
from sqlalchemy import create_engine, text

# ------------------------------------
# HARD-CODED INPUTS (edit as you need)
# ------------------------------------
LATITUDE = 50.45
LONGITUDE = 30.52
START_DATE = "2025-08-01"   # inclusive
END_DATE   = "2025-09-13"   # inclusive
TIMEZONE   = "Europe/Kyiv"

# Base directories (relative to script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_ROOT   = os.path.join(SCRIPT_DIR, "data", "raw")                      # ./data/<day>/response.json
PROC_ROOT  = os.path.join(SCRIPT_DIR, "data", "processed")         # ./data/processed/<day>/data.parquet
DB_PATH    = os.path.join(SCRIPT_DIR, "data", "weather.db")        # ./data/weather.db
SCHEMA_SQL = os.path.join(SCRIPT_DIR, "resources", "sql", "schema.sql")

OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

ALL_DAILY_VARS = [
    "temperature_2m_max", "temperature_2m_min",
    "apparent_temperature_max", "apparent_temperature_min",
    "precipitation_sum", "rain_sum", "showers_sum", "snowfall_sum", "precipitation_hours",
    "sunrise", "sunset", "daylight_duration", "sunshine_duration", "shortwave_radiation_sum",
    "windspeed_10m_max", "windgusts_10m_max", "winddirection_10m_dominant",
    "weathercode", "et0_fao_evapotranspiration",
    "uv_index_max", "uv_index_clear_sky_max",
]

# --------------------------
# HTTP Helpers
# --------------------------
def http_get_with_retries(url, params, max_attempts=5, timeout=60):
    for attempt in range(1, max_attempts + 1):
        try:
            resp = requests.get(url, params=params, timeout=timeout)
            if resp.status_code == 200:
                return resp
            if resp.status_code in (429, 500, 502, 503, 504):
                time.sleep(min(2 ** attempt, 30))
                continue
            return resp
        except requests.RequestException:
            if attempt == max_attempts:
                raise
            time.sleep(min(2 ** attempt, 30))
    raise RuntimeError("Exhausted retries without response")

def parse_unknown_daily_vars(error_text):
    to_remove = set()
    patterns = [
        r"[\"']([a-z0-9_]+)[\"']\s+is not a known variable",
        r"Invalid value for parameter 'daily'[:\s]+([a-z0-9_,\s-]+)",
        r"Unknown daily variables?[:\s]+([a-z0-9_,\s-]+)",
        r"Unsupported daily variables?[:\s]+([a-z0-9_,\s-]+)",
    ]
    for pat in patterns:
        m = re.search(pat, error_text, flags=re.IGNORECASE)
        if m:
            group = m.group(1)
            for token in re.split(r"[,\s]+", group.strip()):
                token = token.strip().lower()
                if token and re.fullmatch(r"[a-z0-9_]+", token):
                    to_remove.add(token)
    return to_remove

def fetch_daily_archive(lat, lon, start_date, end_date, timezone, daily_vars):
    vars_remaining = list(daily_vars)
    removed_all = set()
    while True:
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "timezone": timezone,
            "daily": ",".join(vars_remaining),
        }
        resp = http_get_with_retries(OPEN_METEO_ARCHIVE_URL, params=params)
        if resp.status_code == 200:
            data = resp.json()
            data["_requested_daily"] = daily_vars
            data["_accepted_daily"] = vars_remaining
            data["_dropped_daily"] = sorted(list(removed_all))
            return data

        if resp.status_code == 400:
            try:
                payload = resp.json()
                err_text = json.dumps(payload)
            except Exception:
                err_text = resp.text or ""
            unknown = parse_unknown_daily_vars(err_text)
            if not unknown:
                raise RuntimeError(f"Open-Meteo 400 error: {err_text or 'Bad Request'}")
            vars_remaining = [v for v in vars_remaining if v not in unknown]
            removed_all.update(unknown)
            if not vars_remaining:
                raise RuntimeError(
                    f"All daily variables were rejected by the API. Error: {err_text}"
                )
            continue

        try:
            msg = resp.json()
        except Exception:
            msg = resp.text
        raise RuntimeError(f"Open-Meteo error {resp.status_code}: {msg}")

# --------------------------
# IO Helpers
# --------------------------
def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path

def ensure_raw_outpath(base_dir, day_str):
    out_dir = ensure_dir(os.path.join(base_dir, day_str))
    return os.path.join(out_dir, "response.json")

def ensure_proc_outpath(base_dir, day_str):
    out_dir = ensure_dir(os.path.join(base_dir, day_str))
    return os.path.join(out_dir, "data.parquet")

# --------------------------
# Transform
# --------------------------
def c_to_f(c):
    return None if c is None else (c * 9.0 / 5.0 + 32.0)

def clip_num(x, lo=None, hi=None, none_if_out=True):
    if x is None:
        return None
    try:
        xv = float(x)
    except (TypeError, ValueError):
        return None
    if lo is not None and xv < lo:
        return None if none_if_out else lo
    if hi is not None and xv > hi:
        return None if none_if_out else hi
    return xv

FIELD_MAP = {
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
    "shortwave_radiation_sum": ("shortwave_radiation_mj_m2", lambda v: clip_num(v, 0, None)),
    "windspeed_10m_max": ("wind_max_kmh", lambda v: clip_num(v, 0, 300)),
    "windgusts_10m_max": ("wind_gust_max_kmh", lambda v: clip_num(v, 0, 400)),
    "winddirection_10m_dominant": ("wind_dir_deg", lambda v: clip_num(v, 0, 360)),
    "weathercode": ("weather_code", lambda v: clip_num(v, 0, 99)),
    "et0_fao_evapotranspiration": ("et0_mm", lambda v: clip_num(v, 0, None)),
    "uv_index_max": ("uv_index_max", lambda v: clip_num(v, 0, 25)),
    "uv_index_clear_sky_max": ("uv_index_clear_sky_max", lambda v: clip_num(v, 0, 25)),
}

KEEP_ORDER = [
    "date",
    "temp_max_c", "temp_min_c", "temp_max_f", "temp_min_f",
    "app_temp_max_c", "app_temp_min_c",
    "precip_mm", "rain_mm", "showers_mm", "snowfall_mm", "precip_hours",
    "sunrise", "sunset", "daylight_sec", "sunshine_sec", "shortwave_radiation_mj_m2",
    "wind_max_kmh", "wind_gust_max_kmh", "wind_dir_deg",
    "weather_code",
    "et0_mm",
    "uv_index_max", "uv_index_clear_sky_max",
]

def transform_day_payload(per_day_json):
    d = per_day_json.get("daily", {})
    out = {}
    if isinstance(d.get("time"), list) and d["time"]:
        out["date"] = d["time"][0]

    for in_key, (out_key, cleaner) in FIELD_MAP.items():
        if in_key == "time":
            continue
        val = None
        arr = d.get(in_key)
        if isinstance(arr, list) and arr:
            val = arr[0]
        out[out_key] = cleaner(val)

    out["temp_max_f"] = c_to_f(out.get("temp_max_c"))
    out["temp_min_f"] = c_to_f(out.get("temp_min_c"))

    ordered = {k: out.get(k) for k in KEEP_ORDER}
    for k, v in out.items():
        if k not in ordered:
            ordered[k] = v
    return ordered

# --------------------------
# DB helpers (SQL file + UPSERT)
# --------------------------
def ensure_db_and_table():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    engine = create_engine(f"sqlite:///{DB_PATH}", future=True)

    # Read schema file
    with open(SCHEMA_SQL, "r", encoding="utf-8") as f:
        schema_text = f.read()

    # Use the DBAPI's executescript (handles multi-statement SQL)
    with engine.begin() as conn:
        # Get the underlying sqlite3 connection (SQLAlchemy 2.x)
        raw = conn.connection
        # SQLAlchemy 2.0 provides .driver_connection; fall back for older
        dbapi_conn = getattr(raw, "driver_connection", raw)
        dbapi_conn.executescript(schema_text)

    return engine


UPSERT_SQL = text("""
INSERT INTO weather_daily (
  date, temp_max_c, temp_min_c, temp_max_f, temp_min_f,
  app_temp_max_c, app_temp_min_c,
  precip_mm, rain_mm, showers_mm, snowfall_mm, precip_hours,
  sunrise, sunset, daylight_sec, sunshine_sec, shortwave_radiation_mj_m2,
  wind_max_kmh, wind_gust_max_kmh, wind_dir_deg, weather_code, et0_mm,
  uv_index_max, uv_index_clear_sky_max, source, ingested_at
) VALUES (
  :date, :temp_max_c, :temp_min_c, :temp_max_f, :temp_min_f,
  :app_temp_max_c, :app_temp_min_c,
  :precip_mm, :rain_mm, :showers_mm, :snowfall_mm, :precip_hours,
  :sunrise, :sunset, :daylight_sec, :sunshine_sec, :shortwave_radiation_mj_m2,
  :wind_max_kmh, :wind_gust_max_kmh, :wind_dir_deg, :weather_code, :et0_mm,
  :uv_index_max, :uv_index_clear_sky_max, :source, :ingested_at
)
ON CONFLICT(date) DO UPDATE SET
  temp_max_c=excluded.temp_max_c,
  temp_min_c=excluded.temp_min_c,
  temp_max_f=excluded.temp_max_f,
  temp_min_f=excluded.temp_min_f,
  app_temp_max_c=excluded.app_temp_max_c,
  app_temp_min_c=excluded.app_temp_min_c,
  precip_mm=excluded.precip_mm,
  rain_mm=excluded.rain_mm,
  showers_mm=excluded.showers_mm,
  snowfall_mm=excluded.snowfall_mm,
  precip_hours=excluded.precip_hours,
  sunrise=excluded.sunrise,
  sunset=excluded.sunset,
  daylight_sec=excluded.daylight_sec,
  sunshine_sec=excluded.sunshine_sec,
  shortwave_radiation_mj_m2=excluded.shortwave_radiation_mj_m2,
  wind_max_kmh=excluded.wind_max_kmh,
  wind_gust_max_kmh=excluded.wind_gust_max_kmh,
  wind_dir_deg=excluded.wind_dir_deg,
  weather_code=excluded.weather_code,
  et0_mm=excluded.et0_mm,
  uv_index_max=excluded.uv_index_max,
  uv_index_clear_sky_max=excluded.uv_index_clear_sky_max,
  source=excluded.source,
  ingested_at=excluded.ingested_at;
""")

def df_rows_for_upsert(df: pd.DataFrame):
    """Yield parameter dicts for UPSERT from a one-row DataFrame with known columns."""
    # Normalize/format types:
    rec = df.iloc[0].to_dict()

    # Strings for date/sunrise/sunset (SQLite TEXT)
    # date is yyyy-mm-dd already; ensure that:
    rec["date"] = pd.to_datetime(rec.get("date"), errors="coerce").date().isoformat() if rec.get("date") else None

    for ts_col in ("sunrise", "sunset"):
        v = rec.get(ts_col)
        if pd.isna(v):
            rec[ts_col] = None
        else:
            # If pandas Timestamp, format to ISO string
            if hasattr(v, "isoformat"):
                rec[ts_col] = v.isoformat()
            else:
                rec[ts_col] = str(v)

    # Numerics to plain python types or None
    for num_col in [
        "temp_max_c","temp_min_c","temp_max_f","temp_min_f",
        "app_temp_max_c","app_temp_min_c",
        "precip_mm","rain_mm","showers_mm","snowfall_mm","precip_hours",
        "daylight_sec","sunshine_sec","shortwave_radiation_mj_m2",
        "wind_max_kmh","wind_gust_max_kmh","wind_dir_deg",
        "weather_code","et0_mm","uv_index_max","uv_index_clear_sky_max",
    ]:
        v = rec.get(num_col)
        if pd.isna(v):
            rec[num_col] = None
        else:
            rec[num_col] = float(v) if num_col != "weather_code" else int(v)

    rec["source"] = "open-meteo"
    rec["ingested_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    yield rec

# --------------------------
# Split, Save, and UPSERT (in-memory)
# --------------------------
def split_save_and_upsert(full_json):
    # Ensure dirs
    ensure_dir(RAW_ROOT)
    ensure_dir(PROC_ROOT)

    engine = ensure_db_and_table()

    daily = (full_json or {}).get("daily")
    if not daily or "time" not in daily:
        raise RuntimeError("Response missing 'daily.time' to split by day")

    times = daily["time"]
    n = len(times)

    with engine.begin() as conn:
        for i, day in enumerate(times):
            # ---- Build per-day RAW payload
            per_day = {
                **{k: v for k, v in full_json.items()
                   if k not in ("daily", "hourly", "current", "_requested_daily", "_accepted_daily", "_dropped_daily")},
                "daily": {},
                "_requested_daily": full_json.get("_requested_daily", []),
                "_accepted_daily": full_json.get("_accepted_daily", []),
                "_dropped_daily": full_json.get("_dropped_daily", []),
            }
            for var, arr in daily.items():
                if var == "time":
                    per_day["daily"]["time"] = [day]
                    continue
                if isinstance(arr, list) and len(arr) == n:
                    per_day["daily"][var] = [arr[i]]
                else:
                    per_day["daily"][var] = [None]

            # ---- Save RAW JSON
            raw_path = ensure_raw_outpath(RAW_ROOT, day)
            with open(raw_path, "w", encoding="utf-8") as f:
                json.dump(per_day, f, ensure_ascii=False, indent=2)
            print(f"Saved raw: {raw_path}")

            # ---- Transform to cleaned one-row DataFrame (in memory)
            cleaned = transform_day_payload(per_day)
            df = pd.DataFrame([cleaned])

            # Parse sunrise/sunset to pandas datetime (optional)
            for ts_col in ("sunrise", "sunset"):
                if df[ts_col].notna().any():
                    df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce")

            # ---- Save Parquet (still required)
            proc_path = ensure_proc_outpath(PROC_ROOT, day)
            df.to_parquet(proc_path, index=False, engine="pyarrow")
            print(f"Saved processed: {proc_path}")

            # ---- UPSERT directly from memory (no reading from Parquet)
            params_iter = list(df_rows_for_upsert(df))
            conn.execute(UPSERT_SQL, params_iter)
            print(f"Upserted into SQLite for {day}")

def calculate_metrics():
    Q1 = """
    WITH ordered AS (
      SELECT date, temp_max_c, temp_min_c, precip_mm
      FROM weather_daily
      WHERE date IS NOT NULL
      ORDER BY date
    )
    SELECT
      date,
      AVG(temp_max_c) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS ma7_temp_max_c,
      AVG(temp_min_c) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS ma7_temp_min_c,
      SUM(precip_mm)  OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS sum7_precip_mm
    FROM ordered;
    """

    Q2 = """
    WITH base AS (
      SELECT date, temp_max_c, (temp_max_c >= 30.0) AS is_hot
      FROM weather_daily
      WHERE date IS NOT NULL
    ),
    grp AS (
      SELECT *,
             CASE WHEN is_hot=1 AND LAG(is_hot,1,0) OVER (ORDER BY date)=0 THEN 1 ELSE 0 END AS new_grp
      FROM base
    ),
    grp2 AS (
      SELECT *,
             SUM(new_grp) OVER (ORDER BY date ROWS UNBOUNDED PRECEDING) AS grp_id
      FROM grp
      WHERE is_hot=1
    ),
    streaks AS (
      SELECT
        grp_id,
        MIN(date)       AS start_date,
        MAX(date)       AS end_date,
        COUNT(*)        AS days,
        AVG(temp_max_c) AS avg_temp_max_c,
        MAX(temp_max_c) AS peak_temp_max_c
      FROM grp2
      GROUP BY grp_id
    )
    SELECT *
    FROM streaks
    WHERE days >= 3
    ORDER BY days DESC, start_date;
    """

    Q3 = """
    WITH valid AS (
      SELECT CAST(temp_max_c AS REAL) AS x, CAST(sunshine_sec AS REAL) AS y
      FROM weather_daily
      WHERE temp_max_c IS NOT NULL AND sunshine_sec IS NOT NULL
    ),
    stats AS (
      SELECT
        COUNT(*) AS n,
        AVG(x)   AS mean_x,
        AVG(y)   AS mean_y,
        AVG(x*y) AS mean_xy,
        AVG(x*x) AS mean_x2
      FROM valid
    )
    SELECT
      n,
      (mean_xy - mean_x*mean_y) / NULLIF((mean_x2 - mean_x*mean_x), 0)                            AS beta1_slope,
      (mean_y - ((mean_xy - mean_x*mean_y) / NULLIF((mean_x2 - mean_x*mean_x), 0)) * mean_x)      AS beta0_intercept
    FROM stats;
    """

    engine = create_engine(f"sqlite:///{DB_PATH}", future=True)

    # Run queries
    with engine.begin() as conn:
        df1 = pd.read_sql_query(Q1, conn)
        df2 = pd.read_sql_query(Q2, conn)
        df3 = pd.read_sql_query(Q3, conn)

    # Output dir
    out_dir = os.path.join(SCRIPT_DIR, "data", "reports", datetime.utcnow().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(out_dir, exist_ok=True)

    # JSON: keep structure per section
    report_json = {
        "rolling_7d_metrics": df1.to_dict(orient="records"),
        "heatwave_streaks": df2.to_dict(orient="records"),
        "ols_sunshine_vs_temp": df3.to_dict(orient="records"),
        "_meta": {"generated_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z"}
    }
    json_path = os.path.join(out_dir, "report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_json, f, ensure_ascii=False, indent=2)

    # CSV: concatenate with a section label
    df1c = df1.copy()
    df1c.insert(0, "section", "rolling_7d_metrics")
    df2c = df2.copy()
    df2c.insert(0, "section", "heatwave_streaks")
    df3c = df3.copy()
    df3c.insert(0, "section", "ols_sunshine_vs_temp")
    csv_path = os.path.join(out_dir, "report.csv")
    pd.concat([df1c, df2c, df3c], ignore_index=True, sort=False).to_csv(csv_path, index=False)

    print(f"Wrote {json_path}")
    print(f"Wrote {csv_path}")


# --------------------------
# Main
# --------------------------
def main():
    data = fetch_daily_archive(
        lat=LATITUDE,
        lon=LONGITUDE,
        start_date=START_DATE,
        end_date=END_DATE,
        timezone=TIMEZONE,
        daily_vars=ALL_DAILY_VARS,
    )
    dropped = data.get("_dropped_daily", [])
    if dropped:
        print("Dropped unsupported daily vars:", ", ".join(dropped))
    print("Accepted daily vars:", ", ".join(data.get("_accepted_daily", [])))

    split_save_and_upsert(data)

    calculate_metrics()

if __name__ == "__main__":
    main()
