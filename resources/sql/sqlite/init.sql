-- schema for SQLite database
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS weather_daily (
  date                               DATE PRIMARY KEY,                   -- YYYY-MM-DD
  temp_max_c                         REAL CHECK (temp_max_c > -100 AND temp_max_c < 70),
  temp_min_c                         REAL CHECK (temp_min_c > -120 AND temp_min_c < 70),
  temp_max_f                         REAL,
  temp_min_f                         REAL,
  app_temp_max_c                     REAL CHECK (app_temp_max_c > -120 AND app_temp_max_c < 80),
  app_temp_min_c                     REAL CHECK (app_temp_min_c > -120 AND app_temp_min_c < 80),

  precip_mm                          REAL CHECK (precip_mm >= 0),
  rain_mm                            REAL CHECK (rain_mm >= 0),
  showers_mm                         REAL CHECK (showers_mm >= 0),
  snowfall_mm                        REAL CHECK (snowfall_mm >= 0),
  precip_hours                       REAL CHECK (precip_hours >= 0 AND precip_hours <= 24),

  sunrise                            TEXT,                               -- ISO datetime string (local tz)
  sunset                             TEXT,                               -- ISO datetime string (local tz)
  daylight_sec                       REAL CHECK (daylight_sec >= 0 AND daylight_sec <= 86400),
  sunshine_sec                       REAL CHECK (sunshine_sec >= 0 AND sunshine_sec <= 86400),
  shortwave_radiation_mj_m2          REAL CHECK (shortwave_radiation_mj_m2 >= 0),

  wind_max_kmh                       REAL CHECK (wind_max_kmh >= 0),
  wind_gust_max_kmh                  REAL CHECK (wind_gust_max_kmh >= 0),
  wind_dir_deg                       REAL CHECK (wind_dir_deg >= 0 AND wind_dir_deg <= 360),

  weather_code                       INTEGER CHECK (weather_code BETWEEN 0 AND 99),
  et0_mm                             REAL CHECK (et0_mm >= 0),

  uv_index_max                       REAL CHECK (uv_index_max >= 0),
  uv_index_clear_sky_max             REAL CHECK (uv_index_clear_sky_max >= 0),

  source                             TEXT NOT NULL DEFAULT 'open-meteo',
  ingested_at                        TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Helpful index if you filter by weather code often
CREATE INDEX IF NOT EXISTS idx_weather_daily_code ON weather_daily(weather_code);
