-- Use a Common Table Expression (CTE) to create a daily weather summary
WITH daily_weather_summary AS (
    SELECT
        city_name,
        DATE(forecast_time) AS forecast_day,
        SUM(rainfall_mm) AS total_daily_rainfall,
        MAX(wind_speed_ms) AS max_daily_wind_speed,
        -- Count the number of 3-hour periods with rain
        SUM(CASE WHEN rainfall_mm > 0 THEN 1 ELSE 0 END) AS rainy_periods
    FROM weather_forecasts
    GROUP BY city_name, forecast_day
)
-- Now, join the summary to your orders data
SELECT
    DATE(o.order_date) AS order_day,
    c.city,
    dws.total_daily_rainfall,
    dws.max_daily_wind_speed,
    -- Calculate the risk flags based on the project's criteria
    CASE
        WHEN dws.total_daily_rainfall >= 5 OR dws.rainy_periods >= 3 THEN TRUE
        ELSE FALSE
    END AS rain_risk_flag,
    CASE
        WHEN dws.max_daily_wind_speed >= 10 THEN TRUE
        ELSE FALSE
    END AS wind_risk_flag,
    o.delivery_status
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
-- Join on the city and the date
JOIN daily_weather_summary dws ON c.city = dws.city_name AND DATE(o.order_date) = dws.forecast_day
ORDER BY order_day, c.city;