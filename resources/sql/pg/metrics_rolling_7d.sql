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
