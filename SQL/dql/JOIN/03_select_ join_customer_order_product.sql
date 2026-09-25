SELECT c.name AS customer, p.name AS product_name
FROM customer c
INNER JOIN orders o ON o.customer_id = c.customer_id
INNER JOIN order_item oi ON oi.order_id = o.order_id
INNER JOIN product p ON oi.product_id = p.product_id;