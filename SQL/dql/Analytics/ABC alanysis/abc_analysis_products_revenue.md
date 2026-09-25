# ABC-аналіз товарів за виручкою

**Проєкт:** Pet Shop Analytics (ZOOYUM)
**Тема:** Бізнес-аналітика на реальних даних каталогу
**Файл запиту:** `abc_analysis_products_revenue.sql`

## Бізнес-задача

Мережа має 3513 товарів у каталозі — неможливо приділяти однакову увагу закупівлям, залишкам і просуванню кожного з них. ABC-аналіз ділить товари на три групи за їхнім внеском у загальну виручку мережі:

- **Група A** — нечисленні, але ключові товари, що разом дають перші ~80% виручки. Пріоритет №1 для контролю залишків, закупівель і промо.
- **Група B** — товари середньої важливості, наступні ~15% виручки.
- **Група C** — довгий хвіст товарів, що разом дають лише ~5% виручки. Кандидати на перегляд асортименту.

## Джерела даних

- `product` — довідник товарів (3513 позицій)
- `order_item` — позиції замовлень: `unit_price`, `quantity`, `discount_percent`

Виручка товару рахується як фактична сума продажів з урахуванням знижки, а не за прайсовою ціною (`product.sell_price`):

```
виручка_рядка = unit_price * quantity * (1 - discount_percent / 100)
```

## Методологія

### 1. Сумарна виручка по товару

Групування `order_item` по `product_id` з формулою вище дає загальну виручку кожного товару за весь період.

### 2. Накопичувальний відсоток виручки

Товари сортуються за спаданням виручки (`ORDER BY total_product_revenue DESC`), і для кожного рядка рахується накопичувальна сума через віконну функцію:

```sql
SUM(total_product_revenue) OVER (ORDER BY total_product_revenue DESC)
```

Напрямок сортування тут принциповий: `DESC` означає, що `running_percent` товару показує "яку частку виручки дають цей товар і всі товари, важливіші за нього". Це і є основа класифікації — саме тому товари з найбільшою виручкою отримують найменший накопичувальний відсоток на старті.

### 3. Класифікація A/B/C

За порогом накопичувального відсотка:

- `< 80%` → **A**
- `< 95%` → **B**
- інше → **C**

## SQL

### Запит 1 — товари з накопичувальним відсотком і сегментом

```sql
WITH total_products_revenue AS (
    SELECT p.product_id AS product_id, p.name AS product_name,
           SUM(oi.unit_price * oi.quantity * (1 - oi.discount_percent / 100)) AS total_product_revenue
    FROM product AS p
    JOIN order_item AS oi ON oi.product_id = p.product_id
    GROUP BY p.product_id, p.name
),
with_running_total AS (
    SELECT product_id,
        product_name,
        ROUND(total_product_revenue, 2) AS total_product_revenue,
        ROUND(SUM(total_product_revenue) OVER (ORDER BY total_product_revenue DESC), 2) AS running_total,
        ROUND(SUM(total_product_revenue) OVER (), 2) AS total_revenue
    FROM total_products_revenue
),
with_segment AS (
    SELECT *,
        (running_total * 100) / total_revenue AS running_percent,
        CASE
            WHEN (running_total * 100) / total_revenue < 80 THEN 'A'
            WHEN (running_total * 100) / total_revenue < 95 THEN 'B'
            ELSE 'C'
        END AS price_segment
    FROM with_running_total
)
SELECT product_id,
    product_name,
    total_product_revenue,
    total_revenue,
    price_segment,
    COUNT(*) OVER (PARTITION BY price_segment) AS product_segment_count,
    ROUND((SUM(total_product_revenue) OVER (PARTITION BY price_segment) * 100) / total_revenue, 2) AS segment_percent
FROM with_segment;
```

### Запит 2 — зведення по сегментах (для звіту)

Той самий результат у вигляді короткого підсумку: скільки товарів у кожній групі та яку частку виручки вони дають.

```sql
-- поверх with_segment з запиту 1
SELECT
    price_segment,
    COUNT(*) AS product_count,
    ROUND((SUM(total_product_revenue) * 100) / total_revenue, 2) AS segment_percent
FROM with_segment
GROUP BY price_segment, total_revenue
ORDER BY price_segment;
```

## Ключові рішення та підводні камені

- **Виручка ≠ прайсова ціна.** Рахуємо фактичні продажі зі знижкою (`order_item`), а не каталожну ціну товару.
- **Напрямок `ORDER BY` у вікні визначає сенс накопичувального відсотка.** Без `DESC` накопичувальна сума рахується від найдешевших товарів до найдорожчих, і класифікація втрачає сенс — великий за виручкою товар може опинитись не в групі A лише через порядок обробки рядків.
- **Пороги `CASE` мають відповідати напрямку сортування**, а не бути довільними числами. Стандартні межі 80% / 95% — робоча точка відліку, яку можна коригувати під бізнес-контекст.
- **Дві еквівалентні форми результату:** віконні функції (`PARTITION BY`, без згортання рядків) дають деталізацію на рівні товару зі сегментними метриками поруч; `GROUP BY` дає компактний зведений звіт із трьома рядками. Обидва підходи перевірені на збіг результату.

## Результати

| Сегмент | К-сть товарів | % товарів | % виручки |
|---|---|---|---|
| A | 333 | 22.9% | 79.95% |
| B | 452 | 31.1% | 15.03% |
| C | 668 | 46.0% | 5.01% |

Разом у виборці — 1453 товари, що близько до класичного розподілу 20/30/50 за кількістю при 80/15/5 за виручкою.

**Важливий нюанс:** у каталозі 3513 товарів, але в аналіз потрапило лише 1453 — різниця (2060 товарів, ~59% каталогу) не має жодного рядка в `order_item` за період вибірки, тобто ніколи не продавались. `JOIN` у першому CTE — `INNER JOIN`, тому такі товари мовчки випадають із результату ще до класифікації. Формально вони не є навіть "C" — вони поза межами аналізу. Для повної картини каталогу це окрема, і сама по собі показова, знахідка.

## Наступні кроки

- Маржинальність товарів (`purchase_item.purchase_price` vs `product.sell_price`)
- Оборотність запасів, товари що давно не продавались
