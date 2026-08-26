"""
Генерація orders / order_item для проєкту Pet Shop Analytics.

Логіка обсягу замовлень на день (на магазин):
- База: 10-30 замовлень/день (рандом), помножена на "вагу" магазину
  (частка його асортименту в inventory відносно середнього по мережі).
- Розгін: перші 30 днів - лінійне зростання від ~20% до 100% бази.
- Вихідні (сб/нд): +30-50% до бази.
- Органічне зростання: після розгону +2% до бази щомісяця (тренд).

Клієнти: кожен клієнт має "домашній" магазин (призначається одноразово,
з вагою по розміру магазину). ~5% замовлень - клієнт купує в ІНШОМУ
магазині мережі (не домашньому).

Товари в замовленні обираються лише з тих, що реально є в inventory
магазину (з локального кешу залишків, який скрипт сам зменшує по ходу
генерації - синхронно з тим, що робитиме тригер у реальній базі).

SAVEPOINT перед кожним замовленням - якщо тригер trg_order_product
кине RAISE EXCEPTION (нестача товару), відкочується лише це замовлення,
а не весь прогрес.

Запуск:
    python generate_orders.py
"""

import random
from datetime import date, datetime, timedelta

import psycopg2
import psycopg2.errors

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "pet_shop_test",
    "user": "postgres",
    "password": "admin",
    "client_encoding": "utf8",
}

TODAY = date.today()
START_DATE = TODAY - timedelta(days=182)  # той самий час "відкриття", що й у purchase
RAMP_DAYS = 30

DAILY_ORDERS_RANGE = (10, 30)
WEEKEND_MULTIPLIER_RANGE = (1.3, 1.5)
MONTHLY_GROWTH = 0.02  # +2% на місяць після розгону

ITEMS_PER_ORDER_RANGE = (1, 5)
QTY_PER_ITEM_RANGE = (1, 3)
CROSS_SHOP_PROBABILITY = 0.05
DISCOUNT_CHANCE = 0.2
DISCOUNT_RANGE = (5, 20)
PAYMENT_METHODS = ["Готівка", "Картка", "Безготівковий переказ"]

COMMIT_EVERY_N_ORDERS = 300


def fetch_reference_data(cur):
    cur.execute("SELECT shop_id, name FROM shop;")
    shops = {shop_id: name for shop_id, name in cur.fetchall()}

    cur.execute("SELECT employee_id, shop_id FROM employee;")
    employees_by_shop = {}
    for employee_id, shop_id in cur.fetchall():
        employees_by_shop.setdefault(shop_id, []).append(employee_id)

    cur.execute("SELECT customer_id FROM customer;")
    customers = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT product_id, sell_price FROM product;")
    prices = {product_id: float(sell_price) for product_id, sell_price in cur.fetchall()}

    cur.execute("SELECT shop_id, product_id, quantity FROM inventory;")
    inventory = {}
    for shop_id, product_id, quantity in cur.fetchall():
        inventory[(shop_id, product_id)] = quantity

    return shops, employees_by_shop, customers, prices, inventory


def compute_shop_weights(inventory, shop_ids):
    counts = {shop_id: 0 for shop_id in shop_ids}
    for (shop_id, _), qty in inventory.items():
        if qty > 0:
            counts[shop_id] += 1
    mean_count = sum(counts.values()) / len(counts) if counts else 1
    return {shop_id: (counts[shop_id] / mean_count if mean_count else 1) for shop_id in shop_ids}


def assign_home_shops(customers, shop_ids, shop_weights):
    weights = [shop_weights[s] for s in shop_ids]
    return {customer_id: random.choices(shop_ids, weights=weights, k=1)[0] for customer_id in customers}


def daily_order_count(day_index, is_weekend, shop_weight):
    base = random.uniform(*DAILY_ORDERS_RANGE)

    if day_index < RAMP_DAYS:
        ramp_factor = 0.2 + 0.8 * (day_index / RAMP_DAYS)
    else:
        months_after_ramp = (day_index - RAMP_DAYS) / 30
        ramp_factor = (1 + MONTHLY_GROWTH) ** months_after_ramp

    weekend_factor = random.uniform(*WEEKEND_MULTIPLIER_RANGE) if is_weekend else 1.0

    count = base * ramp_factor * weekend_factor * shop_weight
    return max(0, round(count))


def pick_products_for_order(shop_id, inventory_cache, prices):
    available = [
        pid for (sid, pid), qty in inventory_cache.items()
        if sid == shop_id and qty > 0
    ]
    if not available:
        return []

    n_items = min(random.randint(*ITEMS_PER_ORDER_RANGE), len(available))
    chosen = random.sample(available, n_items)

    items = []
    for product_id in chosen:
        max_qty = inventory_cache[(shop_id, product_id)]
        qty = min(random.randint(*QTY_PER_ITEM_RANGE), max_qty)
        if qty <= 0:
            continue
        unit_price = prices[product_id]
        discount = random.uniform(*DISCOUNT_RANGE) if random.random() < DISCOUNT_CHANCE else 0
        items.append((product_id, qty, unit_price, round(discount, 2)))
        inventory_cache[(shop_id, product_id)] -= qty  # синхронізуємо кеш з тим, що зробить тригер

    return items


def order_status(order_date):
    if (TODAY - order_date).days <= 3:
        return random.choice(["new", "paid"])
    return "delivered"


def insert_order(cur, customer_id, shop_id, employee_id, order_dt, status, total_amount):
    cur.execute(
        """
        INSERT INTO orders
            (customer_id, shop_id, employee_id, order_date, payment_method, status, total_amount)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING order_id;
        """,
        (customer_id, shop_id, employee_id, order_dt, random.choice(PAYMENT_METHODS), status, total_amount),
    )
    return cur.fetchone()[0]


def insert_order_items(cur, order_id, items):
    for product_id, qty, unit_price, discount in items:
        cur.execute(
            """
            INSERT INTO order_item (order_id, product_id, quantity, unit_price, discount_percent)
            VALUES (%s, %s, %s, %s, %s);
            """,
            (order_id, product_id, qty, unit_price, discount),
        )


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    total_orders = 0
    failed_orders = 0
    total_items = 0

    try:
        with conn.cursor() as cur:
            shops, employees_by_shop, customers, prices, inventory_cache = fetch_reference_data(cur)
            shop_ids = list(shops.keys())
            shop_weights = compute_shop_weights(inventory_cache, shop_ids)
            home_shop = assign_home_shops(customers, shop_ids, shop_weights)

            customers_by_shop = {sid: [] for sid in shop_ids}
            for customer_id, sid in home_shop.items():
                customers_by_shop[sid].append(customer_id)

            day_index = 0
            current_day = START_DATE
            while current_day <= TODAY:
                is_weekend = current_day.weekday() >= 5  # 5=субота, 6=неділя

                for shop_id in shop_ids:
                    n_orders = daily_order_count(day_index, is_weekend, shop_weights[shop_id])
                    shop_employees = employees_by_shop.get(shop_id, [])
                    if not shop_employees:
                        continue

                    for _ in range(n_orders):
                        if random.random() < CROSS_SHOP_PROBABILITY:
                            customer_id = random.choice(customers)
                        else:
                            pool = customers_by_shop[shop_id] or customers
                            customer_id = random.choice(pool)

                        cur.execute("SAVEPOINT order_sp;")
                        try:
                            items = pick_products_for_order(shop_id, inventory_cache, prices)
                            if not items:
                                cur.execute("ROLLBACK TO SAVEPOINT order_sp;")
                                continue

                            order_time = datetime.combine(
                                current_day, datetime.min.time()
                            ) + timedelta(hours=random.randint(9, 20), minutes=random.randint(0, 59))

                            total_amount = round(
                                sum(qty * unit_price * (1 - discount / 100) for _, qty, unit_price, discount in items),
                                2,
                            )
                            employee_id = random.choice(shop_employees)
                            status = order_status(current_day)

                            order_id = insert_order(
                                cur, customer_id, shop_id, employee_id, order_time, status, total_amount
                            )
                            insert_order_items(cur, order_id, items)

                            cur.execute("RELEASE SAVEPOINT order_sp;")
                            total_orders += 1
                            total_items += len(items)

                            if total_orders % COMMIT_EVERY_N_ORDERS == 0:
                                conn.commit()
                                print(f"...збережено {total_orders} замовлень")

                        except psycopg2.Error:
                            # відкочуємось ЛИШЕ до SAVEPOINT - решта незакомічених
                            # замовлень у поточному пакеті лишається недоторканою
                            cur.execute("ROLLBACK TO SAVEPOINT order_sp;")
                            failed_orders += 1

                day_index += 1
                current_day += timedelta(days=1)

        conn.commit()
        print(f"\nГотово!")
        print(f"Усього замовлень (orders): {total_orders}")
        print(f"Усього позицій (order_item): {total_items}")
        print(f"Невдалих спроб (rollback): {failed_orders}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()