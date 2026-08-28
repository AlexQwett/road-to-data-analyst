SELECT DATE_TRUNC('month', o.order_date) AS month, COUNT(o.order_id) AS orders_count
FROM orders AS o
GROUP BY month
ORDER BY month;