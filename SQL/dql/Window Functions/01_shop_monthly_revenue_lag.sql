WITH shops_total_revenue AS (
    SELECT s.shop_id, s.name, DATE_TRUNC('month', o.order_date) AS month, SUM(o.total_amount) AS shop_monthly_total_revenue
    FROM shop AS s
    JOIN orders AS o ON o.shop_id = s.shop_id
    GROUP BY s.shop_id, s.name, month
)
SELECT shop_id,
    name, 
    month,
    shop_monthly_total_revenue,
    LAG(shop_monthly_total_revenue) OVER (PARTITION BY shop_id ORDER BY month) AS prev_month_revenue,
    shop_monthly_total_revenue - LAG(shop_monthly_total_revenue) OVER (PARTITION BY shop_id ORDER BY month) AS revenue_change
FROM shops_total_revenue