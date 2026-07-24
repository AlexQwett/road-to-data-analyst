# Database Design

## Product

- product_id (PK)
- name
- category
- brand
- sell_price
- purchase_price
- weight
- created_at
- updated_at
- is_active

---

## Customer

- customer_id (PK)
- name
- phone_number
- email
- birthsday
- discount
- pets_name
- pets_birthsday
- created_at
- updated_at
- is_active

---

## Order
- order_id (PK)
- customer_id (FK)
- shop_id (FK)
- order_date
- payment_method
- status
- total_amount
- created_at

---

## OrderItem
- saleItem_id (PK)
- product_id (FK)
- order_id (FK)
- quantity
- unit_price
- discount
- created_at

---

## Shop
- shop_id (PK)
- address
- created_at
- updated_at
- is_active

---

## Employee
- employee_id (PK)
- position_id (FK)
- shop_id (FK)
- name
- email
- phone_number
- salary
- created_at
- updated_at
- is_active

---

## Position
- position_id
- name
- created_at
- updated_at
- is_active

---

## Provider
- provider_id (PK)
- storage_address
- email
- phone_number
- created_at
- updated_at
- is_active

---

## Inventory
- inventory_id (PK)
- shop_id (FK)
- product_id (FK)
- quantity
- created_at
- updated_at
- is_active


