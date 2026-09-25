WITH employees_total_amount AS (
    SELECT e.employee_id AS employee_id,
        e.shop_id AS employee_shop_id
        e.name AS employee_name,
        SUM(o.total_amount) AS employee_total_amount
    FROM employee AS e
    JOIN orders AS o ON o.employee_id = e.employee_id
    GROUP BY e.employee_id, e.name
)
SELECT employee_name,
    s.name AS shop_name,
    RANK() OVER (PARTITION BY s.shop_id ORDER BY employee_total_amount)
FROM employees_total_amount
JOIN shop AS s ON s.shop_id = employee_shop_id