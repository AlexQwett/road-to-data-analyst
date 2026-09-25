SELECT c.name, COUNT(pet.pet_id)
FROM customer c
LEFT JOIN pet ON pet.customer_id = c.customer_id
GROUP BY c.customer_id;