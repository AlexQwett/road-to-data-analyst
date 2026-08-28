SELECT AVG(oi.discount_percent) AS avg_discount_percent
FROM order_item oi
WHERE oi.discount_percent > 0;