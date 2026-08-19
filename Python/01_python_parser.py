"""
Парсер товарного фіда (Google Merchant XML) -> SQL INSERT для
category / brand / product таблиць проєкту Pet Shop Analytics.

Запуск:
    pip install requests
    python parse_feed.py

Результат:
    product_data_inserts.sql  -- готовий SQL-файл для виконання в PostgreSQL
"""

import re
import xml.etree.ElementTree as ET
import requests

FEED_URL = "https://yumzy.ua/feeds/yumzy.xml"
OUTPUT_FILE = "product_data_inserts.sql"

# Google Merchant namespace
NS = {"g": "http://base.google.com/ns/1.0"}


def escape_sql(value: str) -> str:
    """Екранує одинарні лапки для безпечної вставки в SQL-рядок."""
    return value.replace("'", "''")


def clean_price(raw_price: str) -> str:
    """'744.00 UAH' -> '744.00'"""
    if not raw_price:
        return "0.00"
    match = re.search(r"[\d]+[.,]?\d*", raw_price)
    if not match:
        return "0.00"
    return match.group(0).replace(",", ".")


def extract_category(product_type: str) -> str:
    """
    'Для котів > Корм > Сухий корм' -> 'Корм' (середній рівень)
    Якщо рівнів менше трьох - беремо останній доступний рівень.
    """
    if not product_type:
        return "Інше"
    parts = [p.strip() for p in product_type.split(">")]
    if len(parts) >= 2:
        return parts[1]
    return parts[-1]


def extract_weight_g(title: str):
    """
    Парсить вагу з назви товару.
    Пріоритет: кг/г -> грами. Якщо немає - мл/л -> грами (1мл = 1г).
    Якщо нічого не знайдено (штучні товари: табл, піпетка тощо) -> None.
    """
    if not title:
        return None

    # кг / г
    match = re.search(r"(\d+[.,]?\d*)\s*(кг|г)\b", title, re.IGNORECASE)
    if match:
        value = float(match.group(1).replace(",", "."))
        unit = match.group(2).lower()
        grams = value * 1000 if unit == "кг" else value
        return int(round(grams))

    # л / мл (конвертація 1:1 в грами, за домовленістю)
    match = re.search(r"(\d+[.,]?\d*)\s*(л|мл)\b", title, re.IGNORECASE)
    if match:
        value = float(match.group(1).replace(",", "."))
        unit = match.group(2).lower()
        ml = value * 1000 if unit == "л" else value
        return int(round(ml))

    return None


def main():
    print(f"Завантажую фід: {FEED_URL}")
    response = requests.get(FEED_URL, timeout=30)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    items = root.findall(".//item")
    print(f"Знайдено товарів у фіді: {len(items)}")

    categories = set()
    brands = set()
    products = []  # (name, price, weight_g, category, brand)

    for item in items:
        title = item.findtext("title", default="").strip()
        brand = item.findtext("g:brand", default="", namespaces=NS).strip()
        price = item.findtext("g:price", default="", namespaces=NS).strip()
        product_type = item.findtext("g:product_type", default="", namespaces=NS).strip()

        if not title or not brand:
            # пропускаємо записи без критичних полів
            continue

        category = extract_category(product_type)
        sell_price = clean_price(price)
        weight_g = extract_weight_g(title)

        categories.add(category)
        brands.add(brand)
        products.append((title, sell_price, weight_g, category, brand))

    print(f"Унікальних категорій: {len(categories)}")
    print(f"Унікальних брендів: {len(brands)}")
    print(f"Товарів для вставки: {len(products)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("-- Автоматично згенеровано parse_feed.py\n\n")

        f.write("-- Категорії\n")
        for cat in sorted(categories):
            f.write(
                f"INSERT INTO category (name) VALUES "
                f"('{escape_sql(cat)}') ON CONFLICT (name) DO NOTHING;\n"
            )

        f.write("\n-- Бренди\n")
        for brand in sorted(brands):
            f.write(
                f"INSERT INTO brand (name) VALUES "
                f"('{escape_sql(brand)}') ON CONFLICT (name) DO NOTHING;\n"
            )

        f.write("\n-- Товари\n")
        for name, price, weight_g, category, brand in products:
            weight_sql = "NULL" if weight_g is None else str(weight_g)
            f.write(
                "INSERT INTO product (category_id, brand_id, name, sell_price, weight_g)\n"
                "SELECT c.category_id, b.brand_id, "
                f"'{escape_sql(name)}', {price}, {weight_sql}\n"
                "FROM category c, brand b\n"
                f"WHERE c.name = '{escape_sql(category)}' "
                f"AND b.name = '{escape_sql(brand)}';\n"
            )

    print(f"Готово! SQL-файл збережено: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()