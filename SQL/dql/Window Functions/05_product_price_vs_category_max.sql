SELECT p.product_id AS product_id,
    p.name AS product_name,
    c.name AS category_name,
    p.sell_price AS sell_price,
    MAX(sell_price) OVER (PARTITION BY c.category_id) AS max_category_price,
    p.sell_price - MAX(sell_price) OVER (PARTITION BY c.category_id) AS product_price_vs_category_max
FROM product AS p
JOIN category AS c ON c.category_id = p.category_id