SELECT
    CAST(SUM(CASE WHEN delivery_status = 'On Time' THEN 1 ELSE 0 END) AS REAL) * 100 / COUNT(order_id) AS on_time_delivery_percentage
FROM orders;