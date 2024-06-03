from typing import NewType

import psycopg2


PostgresCursor = NewType("PostgresCursor", psycopg2.extensions.cursor)
PostgresConn = NewType("PostgresConn", psycopg2.extensions.connection)

table_drop_products = "DROP TABLE IF EXISTS products"
table_drop_categories = "DROP TABLE IF EXISTS categories"
table_drop_customers = "DROP TABLE IF EXISTS customers"
table_drop_orders = "DROP TABLE IF EXISTS orders"
table_drop_order_items = "DROP TABLE IF EXISTS order_items"

table_create_categories = """
    CREATE TABLE IF NOT EXISTS categories (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL
    )
"""

table_create_products = """
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        price NUMERIC(10, 2) NOT NULL,
        category_id INTEGER NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories (id)
    )
"""

table_create_customers = """
    CREATE TABLE IF NOT EXISTS customers (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        address TEXT NOT NULL
    )
"""

table_create_orders = """
    CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        order_date DATE NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    )
"""

table_create_order_items = """
    CREATE TABLE IF NOT EXISTS order_items (
        id SERIAL PRIMARY KEY,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
"""

create_table_queries = [
    table_create_categories,
    table_create_products,
    table_create_customers,
    table_create_orders,
    table_create_order_items,
]

drop_table_queries = [
    table_drop_order_items,
    table_drop_orders,
    table_drop_customers,
    table_drop_products,
    table_drop_categories,
]


def drop_tables(cur: PostgresCursor, conn: PostgresConn) -> None:
    """
    Drops each table using the queries in `drop_table_queries` list.
    """
    for query in drop_table_queries:
        cur.execute(query)
        conn.commit()


def create_tables(cur: PostgresCursor, conn: PostgresConn) -> None:
    """
    Creates each table using the queries in `create_table_queries` list.
    """
    for query in create_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    """
    - Establishes connection with the database and gets cursor to it.
    - Drops all the tables.
    - Creates all tables needed.
    - Finally, closes the connection.
    """
    conn = psycopg2.connect(
        "host=localhost dbname=postgres user=postgres password=postgres"
    )
    cur = conn.cursor()

    drop_tables(cur, conn)
    create_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()