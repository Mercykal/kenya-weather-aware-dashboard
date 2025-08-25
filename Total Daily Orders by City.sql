SELECT
    c.city,
    DATE(o.order_date) AS order_day,
    COUNT(o.order_id) AS total_orders
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.city, order_day
ORDER BY order_day, c.city;