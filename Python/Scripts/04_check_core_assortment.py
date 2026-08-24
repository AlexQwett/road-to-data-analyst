"""
Крок 1 (діагностика) для розподілу асортименту магазинів.

Рахує, скільки товарів входить у "ядро" (41 бренд з ручного мапінгу,
60% товарів кожного бренду) і перевіряє, чи воно вміщується в
найменший магазин, перш ніж генерувати щось остаточне.

Запуск:
    python check_core_assortment.py
"""

import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "pet_shop_test",
    "user": "postgres",
    "password": "admin",
    "client_encoding": "utf8",
}

# Ті самі 41 унікальний бренд, що й у ручному мапінгу постачальник-бренд
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

CORE_COVERAGE = 0.6  # 60% товарів кожного бренду входить у ядро

SHOP_TARGETS = {
    "ZOOYUM Набережна": 1200,
    "ZOOYUM Богатирська": 650,
    "ZOOYUM Попова": 550,
    "ZOOYUM Лесі Українки": 400,
}


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT b.name, COUNT(*)
                FROM product p
                JOIN brand b ON b.brand_id = p.brand_id
                WHERE b.name = ANY(%s)
                GROUP BY b.name
                ORDER BY b.name;
                """,
                (CORE_BRANDS,),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    total_core_products = 0
    print(f"{'Бренд':<20} {'Товарів':>8} {'60%':>8}")
    for brand_name, count in rows:
        core_count = round(count * CORE_COVERAGE)
        total_core_products += core_count
        print(f"{brand_name:<20} {count:>8} {core_count:>8}")

    print("-" * 40)
    print(f"Разом у ядрі (60% від {len(rows)} брендів): {total_core_products}")

    smallest_shop = min(SHOP_TARGETS, key=SHOP_TARGETS.get)
    smallest_size = SHOP_TARGETS[smallest_shop]
    print(f"\nНайменший магазин: {smallest_shop} ({smallest_size} товарів)")

    if total_core_products > smallest_size:
        print(
            f"\n⚠️  УВАГА: ядро ({total_core_products}) БІЛЬШЕ за найменший "
            f"магазин ({smallest_size}). Ядро не вміщується для всіх магазинів "
            f"як 'обов'язкове'. Потрібне рішення."
        )
    else:
        print(
            f"\n✅ Ядро ({total_core_products}) вміщується навіть у найменший "
            f"магазин ({smallest_size}). Можна генерувати."
        )


if __name__ == "__main__":
    main()