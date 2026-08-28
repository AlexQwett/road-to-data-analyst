FROM order_item AS oi
JOIN product AS p ON p.product_id = oi.product_id
JOIN brand AS b ON b.brand_id = p.brand_id
GROUP BY b.brand_id
HAVING SUM(oi.unit_price*oi.quantity*(1-oi.discount_percent/100)) > 500000
ORDER BY total_cost DESC;