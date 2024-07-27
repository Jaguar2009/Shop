import sqlite3
from datetime import date

conn = sqlite3.connect('../electronics_store.db')
cursor = conn.cursor()


cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    order_date DATE NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
)
''')

conn.commit()


def add_product(name, category, price):
    if not name or not category or price <= 0:
        print("Неправильні дані для продукту.")
        return
    cursor.execute('''
    INSERT INTO products (name, category, price)
    VALUES (?, ?, ?)
    ''', (name, category, price))
    conn.commit()
    print(f'Продукт "{name}" додано успішно.')


def add_customer(first_name, last_name, email):
    if not first_name or not last_name or not email:
        print("Неправильні дані для клієнта.")
        return
    try:
        cursor.execute('''
        INSERT INTO customers (first_name, last_name, email)
        VALUES (?, ?, ?)
        ''', (first_name, last_name, email))
        conn.commit()
        print(f'Клієнта "{first_name} {last_name}" додано успішно.')
    except sqlite3.IntegrityError:
        print("Клієнт з такою електронною поштою вже існує.")


def add_order(customer_name, product_name, quantity):
    if quantity <= 0:
        print("Кількість повинна бути більшою за нуль.")
        return

    cursor.execute('''
    SELECT customer_id FROM customers
    WHERE first_name || ' ' || last_name = ?
    ''', (customer_name,))
    customer_id = cursor.fetchone()

    if customer_id is None:
        print(f'Клієнта з ім\'ям {customer_name} не знайдено.')
        return

    customer_id = customer_id[0]

    cursor.execute('''
    SELECT product_id FROM products
    WHERE name = ?
    ''', (product_name,))
    product_id = cursor.fetchone()

    if product_id is None:
        print(f'Продукт з назвою {product_name} не знайдено.')
        return

    product_id = product_id[0]

    order_date = date.today().strftime('%Y-%m-%d')
    cursor.execute('''
    INSERT INTO orders (customer_id, product_id, quantity, order_date)
    VALUES (?, ?, ?, ?)
    ''', (customer_id, product_id, quantity, order_date))
    conn.commit()
    print(f'Замовлення на продукт "{product_name}" від клієнта "{customer_name}" додано успішно.')


def total_sales():
    cursor.execute('''
    SELECT SUM(products.price * orders.quantity)
    FROM orders
    JOIN products ON orders.product_id = products.product_id
    ''')
    result = cursor.fetchone()[0]
    if result:
        print(f'Загальний обсяг продажів: {result:.2f} грн')
    else:
        print('Продажі відсутні.')


def orders_per_customer():
    cursor.execute('''
    SELECT customers.first_name, customers.last_name, COUNT(orders.order_id)
    FROM customers
    JOIN orders ON customers.customer_id = orders.customer_id
    GROUP BY customers.customer_id
    ''')
    results = cursor.fetchall()
    for result in results:
        print(f'{result[0]} {result[1]}: {result[2]} замовлень')


def average_order_value():
    cursor.execute('''
    SELECT AVG(products.price * orders.quantity)
    FROM orders
    JOIN products ON orders.product_id = products.product_id
    ''')
    result = cursor.fetchone()[0]
    if result:
        print(f'Середній чек замовлення: {result:.2f} грн')
    else:
        print('Продажі відсутні.')


def most_popular_category():
    cursor.execute('''
    SELECT products.category, COUNT(orders.order_id) AS order_count
    FROM products
    JOIN orders ON products.product_id = orders.product_id
    GROUP BY products.category
    ORDER BY order_count DESC
    LIMIT 1
    ''')
    result = cursor.fetchone()
    if result:
        print(f'Найбільш популярна категорія: {result[0]} з {result[1]} замовленнями')
    else:
        print('Жодної категорії не знайдено.')


def product_count_per_category():
    cursor.execute('''
    SELECT category, COUNT(*) FROM products
    GROUP BY category
    ''')
    results = cursor.fetchall()
    for result in results:
        print(f'{result[0]}: {result[1]} товарів')


def update_smartphone_prices():
    cursor.execute('''
    UPDATE products SET price = price * 1.10 WHERE category = 'смартфони'
    ''')
    conn.commit()
    print('Ціни на смартфони оновлено на 10% збільшення.')


def main():
    while True:
        print("\nВиберіть опцію:")
        print("1. Додати продукт")
        print("2. Додати клієнта")
        print("3. Додати замовлення")
        print("4. Сумарний обсяг продажів")
        print("5. Кількість замовлень на кожного клієнта")
        print("6. Середній чек замовлення")
        print("7. Найбільш популярна категорія товарів")
        print("8. Загальна кількість товарів кожної категорії")
        print("9. Оновити ціни на смартфони")
        print("10. Вийти")

        choice = input("Ваш вибір: ")

        if choice == '1':
            name = input("Назва продукту: ")
            category = input("Категорія: ")
            try:
                price = float(input("Ціна (грн): "))
                add_product(name, category, price)
            except ValueError:
                print("Неправильний формат ціни. Спробуйте ще раз.")
        elif choice == '2':
            first_name = input("Ім'я: ")
            last_name = input("Прізвище: ")
            email = input("Електронна пошта: ")
            add_customer(first_name, last_name, email)
        elif choice == '3':
            customer_name = input("Ім'я клієнта (ім'я прізвище): ")
            product_name = input("Назва продукту: ")
            try:
                quantity = int(input("Кількість: "))
                add_order(customer_name, product_name, quantity)
            except ValueError:
                print("Неправильний формат введення. Спробуйте ще раз.")
        elif choice == '4':
            total_sales()
        elif choice == '5':
            orders_per_customer()
        elif choice == '6':
            average_order_value()
        elif choice == '7':
            most_popular_category()
        elif choice == '8':
            product_count_per_category()
        elif choice == '9':
            update_smartphone_prices()
        elif choice == '10':
            print("Збереження змін та вихід.")
            conn.commit()
            break
        else:
            print("Невірний вибір. Спробуйте ще раз.")


if __name__ == "__main__":
    main()
    conn.close()
