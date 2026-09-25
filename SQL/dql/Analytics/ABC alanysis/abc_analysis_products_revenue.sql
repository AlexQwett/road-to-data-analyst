WITH total_products_revenue AS (
    SELECT p.product_id AS product_id, p.name AS product_name, SUM(oi.unit_price*oi.quantity*(1-oi.discount_percent/100)) AS total_product_revenue
    FROM product AS p
    JOIN order_item AS oi ON oi.product_id = p.product_id
    GROUP BY p.product_id, p.name
),
with_running_total AS (
    SELECT product_id,
        product_name,
        ROUND(total_product_revenue, 2) AS total_product_revenue,
        ROUND(SUM(total_product_revenue) OVER (ORDER BY total_product_revenue DESC), 2) AS running_total,
        ROUND(SUM(total_product_revenue) OVER (), 2) AS total_revenue
    FROM total_products_revenue
)
SELECT *,
    (running_total * 100)/total_revenue AS running_percent,
    CASE 
        WHEN (running_total * 100)/total_revenue < 80 THEN 'A'
        WHEN (running_total * 100)/total_revenue < 95 THEN 'B'
        ELSE 'C'
    END AS price_segment
FROM with_running_total
