"""
Генерація тестових даних customer / pet через Faker.

Запуск:
    pip install Faker
    python generate_customers_pets.py

Результат:
    customer_pet_inserts.sql
"""

import random
from faker import Faker

fake = Faker("uk_UA")
Faker.seed()  # прибери цей рядок, якщо хочеш детермінований (однаковий) результат при кожному запуску

OUTPUT_FILE = "customer_pet_inserts.sql"
CUSTOMER_COUNT = 50

# Розподіл кількості тварин на клієнта: 0 -> 10%, 1 -> 40%, 2 -> 40%, 3 -> 10%
PET_COUNT_CHOICES = [0, 1, 2, 3]
PET_COUNT_WEIGHTS = [10, 40, 40, 10]

# Довідник видів/порід — Faker не вміє генерувати осмислені породи тварин,
# тому цей список ми ведемо самі (куратор), а Faker використовуємо тільки
# для того, де рандом справді доречний (імена, дати).
SPECIES_BREEDS = {
    "Собака": ["Лабрадор", "Такса", "Хаскі", "Мопс", "Німецька вівчарка", "Джек-рассел-тер'єр", "Метис"],
    "Кіт": ["Британська", "Мейн-кун", "Сфінкс", "Шотландська висловуха", "Метис"],
    "Папуга": ["Хвиляста папуга", "Корела", "Ара"],
}

PET_NAMES = [
    "Рекс", "Барсiк", "Мурка", "Кеша", "Багіра", "Джері", "Тобiк", "Лаки",
    "Симба", "Аврора", "Річі", "Стелла", "Марсик", "Зевс", "Кора", "Пушок",
]


def escape_sql(value: str) -> str:
    return value.replace("'", "''")


def gen_phone() -> str:
    return "0" + "".join(random.choices("0123456789", k=9))


def gen_customer_row(used_phones: set):
    name = fake.name()
    phone = gen_phone()
    while phone in used_phones:
        phone = gen_phone()
    used_phones.add(phone)

    # ~20% клієнтів без email (NULL дозволений схемою)
    email = None if random.random() < 0.2 else fake.email()

    # ~15% без дати народження
    birthsday = None if random.random() < 0.15 else fake.date_of_birth(minimum_age=18, maximum_age=75)

    return name, phone, email, birthsday


def gen_pet_row(customer_id: int):
    species = random.choice(list(SPECIES_BREEDS.keys()))
    breed = random.choice(SPECIES_BREEDS[species])
    name = random.choice(PET_NAMES)
    # ~20% без дати народження (власник міг не знати точну дату)
    birthsday = None if random.random() < 0.2 else fake.date_between(start_date="-15y", end_date="today")
    return customer_id, name, species, breed, birthsday


def sql_value(value):
    if value is None:
        return "NULL"
    return f"'{escape_sql(str(value))}'"


def main():
    used_phones = set()
    customers = [gen_customer_row(used_phones) for _ in range(CUSTOMER_COUNT)]

    pets_per_customer = random.choices(PET_COUNT_CHOICES, weights=PET_COUNT_WEIGHTS, k=CUSTOMER_COUNT)
    total_pets = sum(pets_per_customer)

    print(f"Клієнтів: {CUSTOMER_COUNT}")
    print(f"Тварин (за поточним рандомом): {total_pets}")
    print(f"Розподіл тварин по клієнтах: {pets_per_customer}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("-- Автоматично згенеровано generate_customers_pets.py\n\n")
        f.write("-- Клієнти\n")

        for name, phone, email, birthsday in customers:
            f.write(
                "INSERT INTO customer (name, phone_number, email, birthsday) VALUES "
                f"({sql_value(name)}, {sql_value(phone)}, {sql_value(email)}, {sql_value(birthsday)});\n"
            )

        f.write("\n-- Тварини (прив'язка по phone_number клієнта, бо customer_id ще невідомий наперед)\n")
        for (name, phone, _, _), pet_count in zip(customers, pets_per_customer):
            for _ in range(pet_count):
                _, pet_name, species, breed, pet_birthsday = gen_pet_row(None)
                f.write(
                    "INSERT INTO pet (customer_id, name, species, breed, birthsday)\n"
                    f"SELECT customer_id, {sql_value(pet_name)}, {sql_value(species)}, "
                    f"{sql_value(breed)}, {sql_value(pet_birthsday)}\n"
                    f"FROM customer WHERE phone_number = {sql_value(phone)};\n"
                )

    print(f"Готово! SQL-файл збережено: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()