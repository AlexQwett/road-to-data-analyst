"""
Генерація purchase / purchase_item для проєкту Pet Shop Analytics.

Логіка:
1. ВЕЛИКІ поставки: для кожного магазину - по 1 поставці від КОЖНОГО
   з 5 постачальників (80-100 позицій, товари з брендів цього
   постачальника, що входять в асортимент магазину). Дата: 6 місяців тому.
2. ДРІБНІ поставки: 20-30 на магазin, кожна від випадкового
   постачальника, 5-15 позицій, дати розкидані за останні 5 місяців
   (від великої поставки +1 місяць до сьогодні).

Вставки виконуються НАПРЯМУ в базу через psycopg2 - тригер
trg_purchase_product спрацьовує автоматично на кожен INSERT
в purchase_item, і inventory наповнюється сама.

Запуск:
    python generate_purchases.py
"""

import json
import random
from datetime import date, timedelta

import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "pet_shop_test",
    "user": "postgres",
    "password": "admin",
    "client_encoding": "utf8",
}

SHOP_ASSORTMENT_FILE = r"c:\Users\Alex\Desktop\GitHub\road-to-data-analyst\Python\Data\shop_assortment.json"
BRAND_SUPPLIER_FILE = r"c:\Users\Alex\Desktop\GitHub\road-to-data-analyst\Python\Data\brand_supplier_mapping.json"

SUPPLIERS = [
    "ТОВ Спіка", "ТОВ Крайтекс", "ТОВ Рояль Канін",
    "ТОВ Сузір'я", "ТОВ Аскон Зоо Трейд",
]

BIG_DELIVERY_SIZE_RANGE = (80, 100)
SMALL_DELIVERY_COUNT_RANGE = (20, 30)
SMALL_DELIVERY_SIZE_RANGE = (5, 15)
QUANTITY_RANGE = (10, 60)
PAYMENT_METHODS = ["Безготівковий розрахунок", "Готівка", "Передоплата на рахунок"]

TODAY = date.today()
BIG_DATE = TODAY - timedelta(days=182)  # ~6 місяців тому
SMALL_START = BIG_DATE + timedelta(days=30)  # +1 місяць від великої


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_reference_data(cur):
    cur.execute("SELECT shop_id, name FROM shop;")
    shops = {name: shop_id for shop_id, name in cur.fetchall()}

    cur.execute("SELECT supplier_id, name FROM supplier;")
    suppliers = {name: supplier_id for supplier_id, name in cur.fetchall()}

    cur.execute(
        """
        SELECT p.product_id, p.sell_price, b.name
        FROM product p
        JOIN brand b ON b.brand_id = p.brand_id;
        """
    )
    products = {}  # product_id -> (sell_price, brand_name)
    for product_id, sell_price, brand_name in cur.fetchall():
        products[product_id] = (sell_price, brand_name)

    cur.execute("SELECT employee_id, shop_id FROM employee;")
    employees_by_shop = {}
    for employee_id, shop_id in cur.fetchall():
        employees_by_shop.setdefault(shop_id, []).append(employee_id)

    return shops, suppliers, products, employees_by_shop


def build_supplier_brand_products(products, brand_supplier_map):
    """supplier_name -> set(product_id), лише товари брендів цього постачальника"""
    result = {s: set() for s in SUPPLIERS}
    for product_id, (_, brand_name) in products.items():
        for supplier_name in brand_supplier_map.get(brand_name, []):
            if supplier_name in result:
                result[supplier_name].add(product_id)
    return result


def random_purchase_price(sell_price):
    margin_factor = random.uniform(0.5, 0.75)
    price = round(float(sell_price) * margin_factor, 2)
    return max(price, 0.01)


def insert_purchase(cur, shop_id, supplier_id, employee_id, purchase_date, total_amount):
    payment_method = random.choice(PAYMENT_METHODS)
    payment_date = purchase_date + timedelta(days=random.randint(0, 14))
    cur.execute(
        """
        INSERT INTO purchase
            (supplier_id, shop_id, employee_id, purchase_date, status,
             total_amount, payment_date, payment_method)
        VALUES (%s, %s, %s, %s, 'confirmed', %s, %s, %s)
        RETURNING purchase_id;
        """,
        (supplier_id, shop_id, employee_id, purchase_date, total_amount, payment_date, payment_method),
    )
    return cur.fetchone()[0]


def insert_purchase_items(cur, purchase_id, items):
    """items: list of (product_id, purchase_price, quantity)"""
    for product_id, purchase_price, quantity in items:
        cur.execute(
            """
            INSERT INTO purchase_item (purchase_id, product_id, purchase_price, quantity)
            VALUES (%s, %s, %s, %s);
            """,
            (purchase_id, product_id, purchase_price, quantity),
        )


def generate_delivery(cur, shop_id, supplier_id, employee_id, purchase_date, product_pool, products, size_range):
    size = random.randint(*size_range)
    size = min(size, len(product_pool))
    if size == 0:
        return 0

    chosen_products = random.sample(sorted(product_pool), size)
    items = []
    for product_id in chosen_products:
        sell_price, _ = products[product_id]
        purchase_price = random_purchase_price(sell_price)
        quantity = random.randint(*QUANTITY_RANGE)
        items.append((product_id, purchase_price, quantity))

    total_amount = round(sum(p * q for _, p, q in items), 2)
    purchase_id = insert_purchase(cur, shop_id, supplier_id, employee_id, purchase_date, total_amount)
    insert_purchase_items(cur, purchase_id, items)
    return len(items)


def main():
    shop_assortment = load_json(SHOP_ASSORTMENT_FILE)
    brand_supplier_map = load_json(BRAND_SUPPLIER_FILE)

    conn = psycopg2.connect(**DB_CONFIG)
    total_purchases = 0
    total_items = 0
    try:
        with conn.cursor() as cur:
            shops, suppliers, products, employees_by_shop = fetch_reference_data(cur)
            supplier_products = build_supplier_brand_products(products, brand_supplier_map)

            for shop_name, allowed_product_ids in shop_assortment.items():
                shop_id = shops[shop_name]
                allowed_set = set(allowed_product_ids)
                shop_employees = employees_by_shop.get(shop_id, [])
                if not shop_employees:
                    print(f"⚠️  У магазині {shop_name} немає працівників, пропускаю.")
                    continue

                # --- Великі поставки: по 1 від кожного постачальника ---
                for supplier_name in SUPPLIERS:
                    supplier_id = suppliers[supplier_name]
                    pool = supplier_products[supplier_name] & allowed_set
                    employee_id = random.choice(shop_employees)
                    items_count = generate_delivery(
                        cur, shop_id, supplier_id, employee_id, BIG_DATE,
                        pool, products, BIG_DELIVERY_SIZE_RANGE,
                    )
                    if items_count:
                        total_purchases += 1
                        total_items += items_count

                # --- Дрібні поставки ---
                small_count = random.randint(*SMALL_DELIVERY_COUNT_RANGE)
                for _ in range(small_count):
                    supplier_name = random.choice(SUPPLIERS)
                    supplier_id = suppliers[supplier_name]
                    pool = supplier_products[supplier_name] & allowed_set
                    employee_id = random.choice(shop_employees)
                    days_offset = random.randint(0, (TODAY - SMALL_START).days)
                    purchase_date = SMALL_START + timedelta(days=days_offset)

                    items_count = generate_delivery(
                        cur, shop_id, supplier_id, employee_id, purchase_date,
                        pool, products, SMALL_DELIVERY_SIZE_RANGE,
                    )
                    if items_count:
                        total_purchases += 1
                        total_items += items_count

                print(f"{shop_name}: оброблено")

        conn.commit()
        print(f"\nГотово! Усього поставок (purchase): {total_purchases}")
        print(f"Усього позицій (purchase_item): {total_items}")

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()