# Database Design

## product

- product_id (PK)
- category_id (FK)
- brand_id (FK)
- name
- sell_price
- weight_g
- created_at
- updated_at
- is_active

---

## category

- category_id (PK)
- name
- created_at
- updated_at
- is_active

---

## brand

- brand_id (PK)
- name
- created_at
- updated_at
- is_active

---

## customer

- customer_id (PK)
- name
- phone_number
- email
- birthsday
- created_at
- updated_at
- is_active

---

## pet

- pet_id (PK)
- customer_id (FK)
- name
- species
- breed
- pet_birthsday
- created_at
- updated_at
- is_active

---

## order

- order_id (PK)
- customer_id (FK)
- shop_id (FK)
- employee_id (FK)
- order_date
- payment_method
- status
- total_amount
- created_at
- updated_at

---

## order_item

- order_item_id (PK)
- product_id (FK)
- order_id (FK)
- quantity
- unit_price
- discount_percent
- created_at
- updated_at

---

## shop

- shop_id (PK)
- name
- address
- city
- phone_number
- created_at
- updated_at
- is_active

---

## inventory

- inventory_id (PK)
- shop_id (FK)
- product_id (FK)
- quantity
- created_at
- updated_at
- is_active
- UNIQUE (shop_id, product_id)

---

## employee

- employee_id (PK)
- position_id (FK)
- shop_id (FK)
- name
- email
- phone_number
- created_at
- updated_at
- is_active

---

## position

- position_id (PK)
- name
- created_at
- updated_at
- is_active

---

## supplier

- supplier_id (PK)
- name
- contact_person
- address
- email
- phone_number
- created_at
- updated_at
- is_active

---

## purchase

- purchase_id (PK)
- supplier_id (FK)
- shop_id (FK)
- employee_id (FK)
- purchase_date
- status
- total_amount
- payment_date
- payment_method
- created_at
- updated_at

---

## purchase_item

- purchase_item_id (PK)
- purchase_id (FK)
- product_id (FK)
- purchase_price
- quantity
- created_at
- updated_at