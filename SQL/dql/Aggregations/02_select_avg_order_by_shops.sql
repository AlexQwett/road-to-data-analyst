SELECT s.name AS shop_name, ROUND(AVG(o.total_amount), 2) AS avg_order
FROM shop AS s
JOIN orders AS o ON o.shop_id = s.shop_id
GROUP BY s.shop_id