WITH base AS (
  SELECT date, temp_max_c, (temp_max_c >= 30.0) AS is_hot
  FROM weather_daily
  WHERE date IS NOT NULL
),
grp AS (
  SELECT *,
         CASE
           WHEN is_hot AND NOT COALESCE(LAG(is_hot) OVER (ORDER BY date), false)
             THEN 1 ELSE 0
         END AS new_grp
  FROM base
),
grp2 AS (
  SELECT *,
         SUM(new_grp) OVER (ORDER BY date ROWS UNBOUNDED PRECEDING) AS grp_id
  FROM grp
  WHERE is_hot
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
