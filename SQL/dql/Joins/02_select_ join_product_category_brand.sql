SELECT p.name AS product_name, b.name AS brand_name, c.name AS category_name
FROM product p
INNER JOIN brand b ON p.brand_id = b.brand_id
INNER JOIN category c ON p.category_id = c.category_id;