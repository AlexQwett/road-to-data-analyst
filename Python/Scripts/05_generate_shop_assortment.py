"""
Генерація асортименту 4 магазинів для проєкту Pet Shop Analytics.

Логіка:
1. "Ядро" - 60% товарів кожного з 41 "обов'язкового" бренду.
   Це ядро ОДНАКОВЕ і присутнє в асортименті УСІХ 4 магазинів.
2. Кожен магазин доповнюється випадковими товарами (не з ядра),
   щоб досягти свого цільового розміру. Доповнення генерується
   НЕЗАЛЕЖНО для кожного магазину (можливі перетини між магазинами,
   це нормально - товар може бути популярний у кількох точках).

Запуск:
    python generate_shop_assortment.py

Результат:
    shop_assortment.json  -- {shop_name: [product_id, ...]}
"""

import json
import random
import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "pet_shop_test",
    "user": "postgres",
    "password": "admin",
    "client_encoding": "utf8",
}

OUTPUT_FILE = "shop_assortment.json"

CORE_BRANDS = sorted({
    "1st Choice", "Davis", "FoOlee", "Moderna", "Profender", "Pronature",
    "Schesir", "Stefanplast", "Stuzzy", "Wanpy", "Farmina",
    "Home Food", "Joyser", "Monge", "Stronghold", "Stronghold Plus",
    "Royal Canin",
    "Brit", "Canina", "Carnilove", "GimCat", "Half&Half", "ProVET",
    "Savory", "Tetra", "Trixie", "Tropical",
    "ASAN", "Cornelius", "Fine Dog", "Gattino", "Healthy Pet",
    "Kick Tape", "Klicker", "My Food", "Mystic", "Native", "Over Zoo",
    "Palladium", "PawPaw", "Spelly",
})

CORE_COVERAGE = 0.6

SHOP_TARGETS = {
    "ZOOYUM Набережна": 2689,
    "ZOOYUM Богатирська": 2158,
    "ZOOYUM Попова": 1842,
    "ZOOYUM Лесі Українки": 1367,
}


def fetch_products_by_brands(cur, brand_names):
    cur.execute(
        """
        SELECT p.product_id, b.name
        FROM product p
        JOIN brand b ON b.brand_id = p.brand_id
        WHERE b.name = ANY(%s);
        """,
        (brand_names,),
    )
    return cur.fetchall()  # [(product_id, brand_name), ...]


def fetch_all_product_ids(cur):
    cur.execute("SELECT product_id FROM product;")
    return [row[0] for row in cur.fetchall()]


def build_core(cur):
    rows = fetch_products_by_brands(cur, CORE_BRANDS)

    by_brand = {}
    for product_id, brand_name in rows:
        by_brand.setdefault(brand_name, []).append(product_id)

    core_ids = set()
    for brand_name, product_ids in by_brand.items():
        sample_size = round(len(product_ids) * CORE_COVERAGE)
        core_ids.update(random.sample(product_ids, sample_size))

    return core_ids


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            core_ids = build_core(cur)
            all_product_ids = fetch_all_product_ids(cur)
    finally:
        conn.close()

    print(f"Розмір ядра (спільне для всіх магазинів): {len(core_ids)}")

    pool_outside_core = [pid for pid in all_product_ids if pid not in core_ids]

    assortment = {}
    for shop_name, target_size in SHOP_TARGETS.items():
        top_up_size = max(0, target_size - len(core_ids))
        if top_up_size > len(pool_outside_core):
            print(
                f"⚠️  {shop_name}: потрібно {top_up_size} товарів понад ядро, "
                f"але доступно лише {len(pool_outside_core)}. Беремо максимум можливого."
            )
            top_up_size = len(pool_outside_core)

        top_up = random.sample(pool_outside_core, top_up_size)
        shop_products = sorted(core_ids.union(top_up))
        assortment[shop_name] = shop_products

        print(f"{shop_name}: ядро {len(core_ids)} + доповнення {len(top_up)} = {len(shop_products)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(assortment, f, ensure_ascii=False, indent=2)

    print(f"\nГотово! Асортимент збережено: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()