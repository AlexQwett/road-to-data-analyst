SELECT c.name AS category_name, SUM(oi.unit_price*oi.quantity) AS total_cost
FROM order_item AS oi
JOIN product AS p ON p.product_id = oi.product_id
JOIN category AS c ON c.category_id = p.category_id
GROUP BY c.category_id
ORDER BY total_cost DESC
LIMIT 5;