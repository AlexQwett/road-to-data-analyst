SELECT p.product_id AS product_id,
    p.name AS product_name,
    c.name AS category_name,
    p.sell_price AS sell_price,
    MAX(sell_price) OVER (PARTITION BY c.category_id) AS max_category_price,
    p.sell_price - MAX(sell_price) OVER (PARTITION BY c.category_id) AS product_price_vs_category_max,
    FIRST_VALUE(p.name) OVER (PARTITION BY c.category_id ORDER BY p.sell_price DESC) AS most_expensive_product,
    LAST_VALUE(p.name) OVER (
        PARTITION BY c.category_id
        ORDER BY p.sell_price DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS cheapest_product
FROM product AS p
JOIN category AS c ON c.category_id = p.category_id