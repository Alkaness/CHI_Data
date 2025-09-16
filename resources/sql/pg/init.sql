-- Schema for PostgreSQL database

CREATE TABLE IF NOT EXISTS weather_daily (
  date                        DATE PRIMARY KEY,
  temp_max_c                  NUMERIC(5,2),
  temp_min_c                  NUMERIC(5,2),
  temp_max_f                  NUMERIC(5,2),
  temp_min_f                  NUMERIC(5,2),
  app_temp_max_c              NUMERIC(5,2),
  app_temp_min_c              NUMERIC(5,2),
  precip_mm                   NUMERIC(8,2),
  rain_mm                     NUMERIC(8,2),
  showers_mm                  NUMERIC(8,2),
  snowfall_mm                 NUMERIC(8,2),
  precip_hours                NUMERIC(4,2),
  sunrise                     TIMESTAMP WITH TIME ZONE,
  sunset                      TIMESTAMP WITH TIME ZONE,
  daylight_sec                INTEGER,
  sunshine_sec                INTEGER,
  shortwave_radiation_mj_m2   NUMERIC(10,3),
  wind_max_kmh                NUMERIC(6,2),
  wind_gust_max_kmh           NUMERIC(6,2),
  wind_dir_deg                NUMERIC(6,2),
  weather_code                INTEGER,
  et0_mm                      NUMERIC(8,3),
  uv_index_max                NUMERIC(5,2),
  uv_index_clear_sky_max      NUMERIC(5,2),
  source                      TEXT NOT NULL DEFAULT 'open-meteo',
  ingested_at                 TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT chk_temp_max_c CHECK (temp_max_c IS NULL OR (temp_max_c > -100 AND temp_max_c < 70)),
  CONSTRAINT chk_temp_min_c CHECK (temp_min_c IS NULL OR (temp_min_c > -120 AND temp_min_c < 70)),
  CONSTRAINT chk_app_temp_max_c CHECK (app_temp_max_c IS NULL OR (app_temp_max_c > -120 AND app_temp_max_c < 80)),
  CONSTRAINT chk_app_temp_min_c CHECK (app_temp_min_c IS NULL OR (app_temp_min_c > -120 AND app_temp_min_c < 80)),
  CONSTRAINT chk_precip_mm CHECK (precip_mm IS NULL OR precip_mm >= 0),
  CONSTRAINT chk_rain_mm CHECK (rain_mm IS NULL OR rain_mm >= 0),
  CONSTRAINT chk_showers_mm CHECK (showers_mm IS NULL OR showers_mm >= 0),
  CONSTRAINT chk_snowfall_mm CHECK (snowfall_mm IS NULL OR snowfall_mm >= 0),
  CONSTRAINT chk_precip_hours CHECK (precip_hours IS NULL OR (precip_hours >= 0 AND precip_hours <= 24)),
  CONSTRAINT chk_daylight_sec CHECK (daylight_sec IS NULL OR (daylight_sec >= 0 AND daylight_sec <= 86400)),
  CONSTRAINT chk_sunshine_sec CHECK (sunshine_sec IS NULL OR (sunshine_sec >= 0 AND sunshine_sec <= 86400)),
  CONSTRAINT chk_shortwave_radiation CHECK (shortwave_radiation_mj_m2 IS NULL OR shortwave_radiation_mj_m2 >= 0),
  CONSTRAINT chk_wind_max_kmh CHECK (wind_max_kmh IS NULL OR wind_max_kmh >= 0),
  CONSTRAINT chk_wind_gust_max_kmh CHECK (wind_gust_max_kmh IS NULL OR wind_gust_max_kmh >= 0),
  CONSTRAINT chk_wind_dir_deg CHECK (wind_dir_deg IS NULL OR (wind_dir_deg >= 0 AND wind_dir_deg <= 360)),
  CONSTRAINT chk_weather_code CHECK (weather_code IS NULL OR weather_code BETWEEN 0 AND 99),
  CONSTRAINT chk_et0_mm CHECK (et0_mm IS NULL OR et0_mm >= 0),
  CONSTRAINT chk_uv_index_max CHECK (uv_index_max IS NULL OR uv_index_max >= 0),
  CONSTRAINT chk_uv_index_clear_sky_max CHECK (uv_index_clear_sky_max IS NULL OR uv_index_clear_sky_max >= 0)
);

CREATE INDEX IF NOT EXISTS idx_weather_daily_code ON weather_daily(weather_code);

CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.ingested_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_weather_daily_ingested_at ON weather_daily;

CREATE TRIGGER update_weather_daily_ingested_at
BEFORE UPDATE ON weather_daily
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();

COMMENT ON TABLE weather_daily IS 'Daily weather data from Open-Meteo API';
COMMENT ON COLUMN weather_daily.date IS 'Date of the weather record (YYYY-MM-DD)';
COMMENT ON COLUMN weather_daily.temp_max_c IS 'Maximum temperature in Celsius';
COMMENT ON COLUMN weather_daily.temp_min_c IS 'Minimum temperature in Celsius';
COMMENT ON COLUMN weather_daily.temp_max_f IS 'Maximum temperature in Fahrenheit';
COMMENT ON COLUMN weather_daily.temp_min_f IS 'Minimum temperature in Fahrenheit';
COMMENT ON COLUMN weather_daily.app_temp_max_c IS 'Apparent (feels-like) maximum temperature in Celsius';
COMMENT ON COLUMN weather_daily.app_temp_min_c IS 'Apparent (feels-like) minimum temperature in Celsius';
COMMENT ON COLUMN weather_daily.precip_mm IS 'Total precipitation in millimeters';
COMMENT ON COLUMN weather_daily.rain_mm IS 'Rainfall in millimeters';
COMMENT ON COLUMN weather_daily.showers_mm IS 'Shower precipitation in millimeters';
COMMENT ON COLUMN weather_daily.snowfall_mm IS 'Snowfall in millimeters';
COMMENT ON COLUMN weather_daily.precip_hours IS 'Number of hours with precipitation';
COMMENT ON COLUMN weather_daily.sunrise IS 'Sunrise time (timestamp with timezone)';
COMMENT ON COLUMN weather_daily.sunset IS 'Sunset time (timestamp with timezone)';
COMMENT ON COLUMN weather_daily.daylight_sec IS 'Daylight duration in seconds';
COMMENT ON COLUMN weather_daily.sunshine_sec IS 'Sunshine duration in seconds';
COMMENT ON COLUMN weather_daily.shortwave_radiation_mj_m2 IS 'Shortwave solar radiation in megajoules per square meter';
COMMENT ON COLUMN weather_daily.wind_max_kmh IS 'Maximum wind speed in kilometers per hour';
COMMENT ON COLUMN weather_daily.wind_gust_max_kmh IS 'Maximum wind gust speed in kilometers per hour';
COMMENT ON COLUMN weather_daily.wind_dir_deg IS 'Wind direction in degrees (0-360)';
COMMENT ON COLUMN weather_daily.weather_code IS 'WMO weather code (0-99)';
COMMENT ON COLUMN weather_daily.et0_mm IS 'Reference evapotranspiration in millimeters';
COMMENT ON COLUMN weather_daily.uv_index_max IS 'Maximum UV index';
COMMENT ON COLUMN weather_daily.uv_index_clear_sky_max IS 'Maximum UV index under clear sky conditions';
COMMENT ON COLUMN weather_daily.source IS 'Data source identifier';
COMMENT ON COLUMN weather_daily.ingested_at IS 'Timestamp when the record was last updated';
