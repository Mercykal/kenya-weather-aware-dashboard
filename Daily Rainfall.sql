SELECT
    city_name,
    DATE(forecast_time) AS forecast_day,
    SUM(rainfall_mm) AS total_daily_rainfall
FROM weather_forecasts
GROUP BY city_name, forecast_day
ORDER BY forecast_day, city_name;