WITH shop_avg AS (
    SELECT s.shop_id, s.name, AVG(o.total_amount) AS avg_shop_amount
    FROM shop AS s
    JOIN orders AS o ON o.shop_id = s.shop_id
    GROUP BY s.shop_id, s.name
),
network_avg AS (
    SELECT AVG(total_amount) AS avg_network_total_amount
    FROM orders
)
SELECT shop_id, name, avg_shop_amount, avg_network_total_amount 
FROM shop_avg, network_avg
WHERE avg_shop_amount > avg_network_total_amount