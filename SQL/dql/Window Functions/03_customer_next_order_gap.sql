WITH customer_next_order_gap AS (
    SELECT COUNT(*) OVER (PARTITION BY c.customer_id) AS orders_count,
        c.name AS customer_name,
        o.order_id AS order_id,
        o.order_date AS order_date,
        LEAD(o.order_date) OVER (PARTITION BY c.customer_id ORDER BY o.order_date) AS next_order_date,
        EXTRACT(DAY FROM LEAD(o.order_date) OVER (PARTITION BY c.customer_id ORDER BY o.order_date) - o.order_date) AS gap
    FROM customer AS c
    JOIN orders AS o ON o.customer_id = c.customer_id
)
SELECT *
FROM customer_next_order_gap
WHERE orders_count >= 2