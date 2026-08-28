SELECT p.name AS product_name, SUM(oi.quantity) AS total_quantity
FROM product AS p
JOIN order_item AS oi ON oi.product_id = p.product_id
GROUP BY p.product_id
ORDER BY total_quantity DESC
LIMIT 10;