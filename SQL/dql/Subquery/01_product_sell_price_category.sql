SELECT COUNT(p.product_id) AS product_count,
    CASE 
        WHEN p.sell_price < 200 THEN 'Дешевий'
        WHEN p.sell_price < 1000 THEN 'Бюджетний'
        WHEN p.sell_price < 3000 THEN 'Дорогий'
        ELSE 'Дуже дорогий'
    END AS price_segment
FROM product AS p
GROUP BY price_segment