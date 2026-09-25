SELECT p.name AS product_name, b.name AS brand_name
FROM product p
INNER JOIN brand b on p.brand_id = b.brand_id