WITH product_price_rank_by_category AS (
    SELECT p.name AS product_name,
        c.name AS category_name,
        p.sell_price AS product_price,
        RANK() OVER (PARTITION BY c.category_id ORDER BY p.sell_price DESC) AS product_rank
    FROM product AS p
    JOIN category AS c ON c.category_id = p.category_id
)
SELECT *
FROM product_price_rank_by_category
WHERE product_rank <= 3
