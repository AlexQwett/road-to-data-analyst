"""
Генерація мапінгу supplier -> [brands] для проєкту Pet Shop Analytics.

Ручні прив'язки (задані свідомо, з навмисними перекриттями) + решта
брендів, яких немає в базі, розподіляються випадково між 4 "загальними"
постачальниками (Royal Canin лишається ексклюзивом ТОВ Рояль Канін).

Запуск:
    pip install psycopg2-binary
    python 03_python_brand_mapping.py

Результат:
    brand_supplier_mapping.json  -- фінальний мапінг для використання
                                     в генераторі purchase/purchase_item
"""

import json
import random
import psycopg2

# --- Налаштування підключення до бази - заповни своїми даними ---
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "pet_shop_test",   # напр. "pet_shop_test"
    "user": "postgres",     # напр. "postgres"
    "password": "admin",
    "client_encoding": "utf8",
}

OUTPUT_FILE = "brand_supplier_mapping.json"

# Ручний мапінг: постачальник -> список брендів (за твоїм рішенням)
MANUAL_MAPPING = {
    "ТОВ Спіка": [
        "1st Choice", "Davis", "FoOlee", "Moderna", "Profender", "Pronature",
        "Schesir", "Stefanplast", "Stuzzy", "Wanpy", "Farmina",
    ],
    "ТОВ Крайтекс": [
        "Home Food", "Joyser", "Monge", "Stronghold", "Stronghold Plus", "Farmina",
    ],
    "ТОВ Рояль Канін": ["Royal Canin"],
    "ТОВ Сузір'я": [
        "Brit", "Canina", "Carnilove", "GimCat", "Half&Half", "ProVET",
        "Savory", "Stronghold", "Stronghold Plus", "Tetra", "Trixie", "Tropical",
    ],
    "ТОВ Аскон Зоо Трейд": [
        "ASAN", "Cornelius", "Fine Dog", "Gattino", "Healthy Pet", "Home Food",
        "Kick Tape", "Klicker", "My Food", "Mystic", "Native", "Over Zoo",
        "Palladium", "PawPaw", "Spelly", "Trixie",
    ],
}

# "Загальні" постачальники, серед яких розподіляються нерозподілені бренди
# (Рояль Канін навмисно виключений - залишається ексклюзивом Royal Canin)
GENERAL_SUPPLIERS = ["ТОВ Спіка", "ТОВ Крайтекс", "ТОВ Сузір'я", "ТОВ Аскон Зоо Трейд"]

# Ймовірність, що нерозподілений бренд отримає ДРУГОГО постачальника (перекриття)
OVERLAP_PROBABILITY = 0.1


def fetch_all_brands():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM brand ORDER BY name;")
            return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()


def main():
    all_brands = fetch_all_brands()
    print(f"Усього брендів у базі: {len(all_brands)}")

    # Зібрати вже розподілені бренди (з ручного мапінгу)
    assigned_brands = set()
    for brands in MANUAL_MAPPING.values():
        assigned_brands.update(brands)

    unassigned = [b for b in all_brands if b not in assigned_brands]
    print(f"Уже розподілено вручну: {len(assigned_brands)}")
    print(f"Залишилось розподілити випадково: {len(unassigned)}")

    # Фінальний мапінг: brand -> [suppliers]
    brand_to_suppliers = {}
    for supplier, brands in MANUAL_MAPPING.items():
        for brand in brands:
            brand_to_suppliers.setdefault(brand, []).append(supplier)

    # Випадковий розподіл нерозподілених брендів
    for brand in unassigned:
        primary = random.choice(GENERAL_SUPPLIERS)
        suppliers = [primary]
        if random.random() < OVERLAP_PROBABILITY:
            secondary_options = [s for s in GENERAL_SUPPLIERS if s != primary]
            suppliers.append(random.choice(secondary_options))
        brand_to_suppliers[brand] = suppliers

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(brand_to_suppliers, f, ensure_ascii=False, indent=2)

    print(f"Готово! Мапінг збережено: {OUTPUT_FILE}")
    print(f"Усього брендів у фінальному мапінгу: {len(brand_to_suppliers)}")


if __name__ == "__main__":
    main()