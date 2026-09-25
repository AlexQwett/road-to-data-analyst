SELECT s.name AS shop_name, DATE_TRUNC('month', o.order_date) AS month, ROUND(SUM(oi.unit_price*oi.quantity*(1-oi.discount_percent/100)), 2) AS total_cost
FROM shop AS s
JOIN orders AS o ON o.shop_id = s.shop_id
JOIN order_item AS oi ON oi.order_id = o.order_id
GROUP BY s.shop_id, month
ORDER BY s.name, month DESC;