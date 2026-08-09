# Table Documentation

## category

### Purpose

Saves basic information about category

### Fields

| Field | Type | Description | Rules |
|---|---|---|---|
| category_id | BIGINT | Unique identifier of category | PK, Identity |
| name | TEXT | Category name | NOT NULL |
| created_at | TIMESTAMP | Date and time of creation of the record | NOT NULL, DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | Date and time of last edit | NULL |
| is_active | BOOLEAN | Is active category | NOT NULL, DEFAULT TRUE |

### Business Rules

- One category has many products.




## brand

### Purpose

Saves basic information about brand.

### Fields

| Field | Type | Description | Rules |
|---|---|---|---|
| brand_id | BIGINT | Unique identifier of brand | PK, Identity |
| name | TEXT | Brand name | NOT NULL |
| created_at | TIMESTAMP | Date and time of creation of the record | NOT NULL, DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | Date and time of last edit | NULL |
| is_active | BOOLEAN | Is active brand | NOT NULL, DEFAULT TRUE |

### Business Rules

- One brand has many products.




## product

### Purpose

Saves basic information about product.

### Fields

| Field | Type | Description | Rules |
|---|---|---|---|
| product_id | BIGINT | Unique identifier of product | PK, Identity |
| category_id | BIGINT | Unique identifier of product category | FK → category.category_id |
| brand_id | BIGINT | Unique identifier of product brand | FK → brand.brand_id |
| name | TEXT | Product name | NOT NULL |
| sell_price | NUMERIC(10,2) | Current selling price | NOT NULL, >= 0 |
| weight_g | INTEGER | Product weight in grams | NOT NULL, > 0 |
| created_at | TIMESTAMP | Date and time of creation of the record | NOT NULL, DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | Date and time of last edit | NULL |
| is_active | BOOLEAN | Is active product | NOT NULL, DEFAULT TRUE |

### Business Rules

- One product belongs to one category.
- One product belongs to one brand.
- One product has many order item.
- One product has many purchase item.
- One product has many inventory.
- A product may be available in several stores. 
- The purchase price is not saved in `product` because it depends on the batch.




## customer

### Purpose

Saves basic information about customer.

### Fields

| Field | Type | Description | Rules |
|---|---|---|---|
| customer_id | BIGINT | Unique identifier of customer | PK, Identity |
| name | TEXT | Customer name | NOT NULL |
| phone_number | TEXT | Customer phone number | UNIQUE, NOT NULL |
| email | TEXT | Customer email | NULL |
| birthsday | DATE | Customer birthsday | NOT NULL |
| created_at | TIMESTAMP | Date and time of creation of the record | NOT NULL, DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | Date and time of last edit | NULL |
| is_active | BOOLEAN | Is active customer | NOT NULL, DEFAULT TRUE |

### Business Rules

- One customer has many pets.
- Unique customer phone number. Family members can't use the same phone number.
- Email null. Not all customers have email.




## pet

### Purpose

Saves basic information about pet of customer.

### Fields

| Field | Type | Description | Rules |
|---|---|---|---|
| pet_id | BIGINT | Unique identifier of pet | PK, Identity |
| customer_id | BIGINT | Unique pet owner (customer) identifier | FK → customer.customer_id |
| name | TEXT | Pet name | NOT NULL |
| species | TEXT | A specie of pet | NOT NULL |
| breed | TEXT | A breed of pet | NOT NULL |
| birthsday | DATE | Pet birthsday | NULL |
| created_at | TIMESTAMP | Date and time of creation of the record | NOT NULL, DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | Date and time of last edit | NULL |
| is_active | BOOLEAN | Is active pet | NOT NULL, DEFAULT TRUE |

### Business Rules

- Many pets belong to one customer.
- Not all customers know their pet's birthday.




## shop

### Purpose

Saves basic information about shop.

### Fields

| Field | Type | Description | Rules |
|---|---|---|---|
| shop_id | BIGINT | Unique identifier of shop | PK, Identity |
| name | TEXT | Shop name | NOT NULL |
| address | TEXT | Shop address | NOT NULL |
| city | TEXT | Сity where the shop is located | NOT NULL |
| phone | TEXT | Shop phone number | NOT NULL |
| created_at | TIMESTAMP | Date and time of creation of the record | NOT NULL, DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | Date and time of last edit | NULL |
| is_active | BOOLEAN | Is active shop | NOT NULL, DEFAULT TRUE |

### Business Rules

- One shop has many orders.
- One shop has many inventories.
- One shop has many emloyee.
- One shop has many purchase.




## position

### Purpose

Saves basic information about employee position.

### Fields

| Field | Type | Description | Rules |
|---|---|---|---|
| position_id | BIGINT | Unique identifier of position | PK, Identity |
| name | TEXT | Shop name | NOT NULL |
| created_at | TIMESTAMP | Date and time of creation of the record | NOT NULL, DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | Date and time of last edit | NULL |
| is_active | BOOLEAN | Is active position | NOT NULL, DEFAULT TRUE |

### Business Rules

- One position has many employees.




## employee

### Purpose

Saves basic information about employee.

### Fields

| Field | Type | Description | Rules |
|---|---|---|---|
| employee_id | BIGINT | Unique identifier of employee | PK, Identity |
| position_id | BIGINT | Unique employee position identifier | FK → position.position_id |
| shop_id | BIGINT | Unique identifier of the store where the employee works | FK → shop.shop_id |
| name | TEXT | Employee name | NOT NULL |
| email | TEXT | Employee email | NOT NULL |
| phone | TEXT | Employee phone | NOT NULL |
| created_at | TIMESTAMP | Date and time of creation of the record | NOT NULL, DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | Date and time of last edit | NULL |
| is_active | BOOLEAN | Is active employee | NOT NULL, DEFAULT TRUE |

### Business Rules

- One employee has many orders.
- One employee has many purchases.




## order

### Purpose

Saves information about order.

### Fields

| Field | Type | Description | Rules |
|---|---|---|---|
| order_id | BIGINT | Unique identifier of order | PK, Identity |
| customer_id | BIGINT | Unique customer identifier | FK → customer.customer_id |
| shop_id | BIGINT | Unique shops order identifier | FK → shop.shop_id |
| employee_id | BIGINT | Unique shops employee identifier | FK → employee.employee_id |
| order_date | TIMESTAMP | Date and time of order creation | NOT NULL, DEFAULT CURRENT_TIMESTAMP |
| payment_method | TEXT | Payment method of order | NOT NULL |
| status | TEXT | Order status | NOT NULL |
| total_amount | NUMERIC(10,2) | Order total amount | NOT NULL, >= 0 |
| created_at | TIMESTAMP | Date and time of creation of the record | NOT NULL, DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | Date and time of last edit | NULL |

### Business Rules

- One order has many order items.
- total_amount must be a NUMERIC(10,2) same as product price.




## order_item

### Purpose

Saves information about order item.

### Fields

| Field | Type | Description | Rules |
|---|---|---|---|
| order_item_id | BIGINT | Unique identifier of order item | PK, Identity |
| product_id | BIGINT | Unique product identifier | FK → product.product_id |
| order_id | BIGINT | Unique order identifier | FK → order.order_id |
| quantity | INTEGER | Quantity of product | NOT NULL, > 0 |
| unit_price | NUMERIC(10,2) | Product price | NOT NULL, >= 0 |
| discount_percent | NUMERIC(5,2) | Product discount | NOT NULL, >= 0, DEFAULT 0|
| created_at | TIMESTAMP | Date and time of creation of the record | NOT NULL, DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | Date and time of last edit | NULL |

### Business Rules

- Many order items belong to one order.
- Many order item belong to one product.
- unit_price must be a NUMERIC(10,2) same as product price.




## supplier

### Purpose

Saves information about supplier.

### Fields

| Field | Type | Description | Rules |
|---|---|---|---|
| supplier_id | BIGINT | Unique identifier of supplier | PK, Identity |
| name | TEXT | Name of supplier company | NOT NULL |
| contact_person | TEXT | Name of supplier contact person | NOT NULL |
| address | TEXT | Supplier address | NOT NULL |
| email | TEXT | Supplier email | NOT NULL |
| phone | TEXT | Supplier phone | NOT NULL |
| created_at | TIMESTAMP | Date and time of creation of the record | NOT NULL, DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | Date and time of last edit | NULL |
| is_active | BOOLEAN | Is active supplier | NOT NULL, DEFAULT TRUE |

### Business Rules

- One supplier has many purchase.




## purchase

### Purpose

Saves information about purchase.

### Fields

| Field | Type | Description | Rules |
|---|---|---|---|
| purchase_id | BIGINT | Unique identifier of supplier | PK, Identity |
| supplier_id | BIGINT | Unique supplier identifier | FK → supplier.supplier_id |
| shop_id | BIGINT | Unique shop to purchase identifier | FK → shop.shop_id |
| employee_id | BIGINT | Unique responsible employee for purchase identifier | FK → employee.employee_id |
| purchase_date | DATE | Date of purchase creation | NOT NULL, DEFAULT CURRENT_TIMESTAMP |
| status | TEXT | Purchase status | NOT NULL |
| total_amount | NUMERIC(10,2) | Purchase total amount | NOT NULL, >= 0 |
| payment_date | TIMESTAMP | Date and time of purchase pay | NULL |
| payment_method | TEXT | Payment method of purchase | NOT NULL |
| created_at | TIMESTAMP | Date and time of creation of the record | NOT NULL, DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | Date and time of last edit | NULL |

### Business Rules

- One purchase has many purchase_item.
- total_amount must be a NUMERIC(10,2) same as product price.




## purchase_item

### Purpose

Saves information about purchase item.

### Fields

| Field | Type | Description | Rules |
|---|---|---|---|
| purchase_item_id | BIGINT | Unique identifier of purchase item | PK, Identity |
| purchase_id | BIGINT | Unique purchase identifier | FK → purchase.purchase_id |
| product_id | BIGINT | Unique product to purchase identifier | FK → product.product_id |
| purchase_price | NUMERIC(10,2) | Purchase price | NOT NULL, > 0 |
| quantity | INTEGER | Quantity of product | NOT NULL |
| created_at | TIMESTAMP | Date and time of creation of the record | NOT NULL, DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | Date and time of last edit | NULL |

### Business Rules

- Many purchase items belong to one purchase.
- purchase_price must be a NUMERIC(10,2) same as product price.




## inventory

### Purpose

Saves information about shop inventory.

### Fields

| Field | Type | Description | Rules |
|---|---|---|---|
| inventory_id | BIGINT | Unique identifier of inventory | PK, Identity |
| shop_id | BIGINT | Unique shop inventory identifier | FK → shop.shop_id, UNIQUE(shop_id, product_id) |
| product_id | BIGINT | Unique product identifier in shop inventory | FK → product.product_id, UNIQUE(shop_id, product_id) |
| quantity | INTEGER | Quantity of product | NOT NULL |
| created_at | TIMESTAMP | Date and time of creation of the record | NOT NULL, DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | Date and time of last edit | NULL |
| is_active | BOOLEAN | Is active product | NOT NULL, DEFAULT TRUE |

### Business Rules

- "Inventory" is needed for checking stock of product in shop.
- To avoid duplication of product availability in one store, there is a condition UNIQUE(shop_id, product_id).