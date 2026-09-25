SELECT p.name, p.sell_price, p.category_id
FROM product AS p
WHERE p.sell_price > (
    SELECT AVG(sell_price)
    FROM product
    WHERE category_id = p.category_id
);