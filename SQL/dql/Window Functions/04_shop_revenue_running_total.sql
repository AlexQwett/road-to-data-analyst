WITH shops_month_total_revenue AS (
    SELECT s.shop_id AS shop_id,
    s.name AS shop_name,
    DATE_TRUNC('month', o.order_date) AS month,
    SUM(o.total_amount) AS shop_month_total_revenue
FROM shop AS s
JOIN orders AS o ON o.shop_id = s.shop_id
GROUP BY s.shop_id, month
)
SELECT shop_id,
    shop_name,
    month,
    shop_month_total_revenue,
    SUM(shop_month_total_revenue) OVER (PARTITION BY shop_id ORDER BY month) AS running_total_revenue
FROM shops_month_total_revenue