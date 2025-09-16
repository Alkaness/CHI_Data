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
