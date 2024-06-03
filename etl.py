import glob
import json
import os
from typing import List

import psycopg2


def get_files(filepath: str) -> List[str]:
    """
    Description: This function is responsible for listing the files in a directory
    """

    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root, "*.json"))
        for f in files:
            all_files.append(os.path.abspath(f))

    num_files = len(all_files)
    print(f"{num_files} files found in {filepath}")

    return all_files


def process(cur, conn, filepath):
    # Get list of files from filepath
    all_files = get_files(filepath)

    for datafile in all_files:
        with open(datafile, "r") as f:
            data = json.loads(f.read())
            for item in data:
                # Insert data into the categories table
                insert_statement = """
                    INSERT INTO categories (name)
                    VALUES (%(name)s)
                    ON CONFLICT (name) DO NOTHING
                """
                cur.execute(insert_statement, {"name": item["category"]})

                # Get the category_id for the inserted category
                select_statement = """
                    SELECT id FROM categories WHERE name = %(name)s
                """
                cur.execute(select_statement, {"name": item["category"]})
                category_id = cur.fetchone()[0]

                # Insert data into the products table
                insert_statement = """
                    INSERT INTO products (name, price, category_id)
                    VALUES (%(name)s, %(price)s, %(category_id)s)
                    ON CONFLICT (name) DO NOTHING
                """
                cur.execute(insert_statement, {"name": item["product_name"], "price": item["price"], "category_id": category_id})

                # Insert data into the customers table
                insert_statement = """
                    INSERT INTO customers (name, email, address)
                    VALUES (%(name)s, %(email)s, %(address)s)
                    ON CONFLICT (email) DO NOTHING
                """
                cur.execute(insert_statement, {"name": item["customer_name"], "email": item["customer_email"], "address": item["customer_address"]})

                # Get the customer_id for the inserted customer
                select_statement = """
                    SELECT id FROM customers WHERE email = %(email)s
                """
                cur.execute(select_statement, {"email": item["customer_email"]})
                customer_id = cur.fetchone()[0]

                # Insert data into the orders table
                insert_statement = """
                    INSERT INTO orders (customer_id, order_date)
                    VALUES (%(customer_id)s, %(order_date)s)
                    RETURNING id
                """
                cur.execute(insert_statement, {"customer_id": customer_id, "order_date": item["order_date"]})
                order_id = cur.fetchone()[0]

                # Insert data into the order_items table
                for product in item["products"]:
                    select_statement = """
                        SELECT id FROM products WHERE name = %(name)s
                    """
                    cur.execute(select_statement, {"name": product["product_name"]})
                    product_id = cur.fetchone()[0]

                    insert_statement = """
                        INSERT INTO order_items (order_id, product_id, quantity)
                        VALUES (%(order_id)s, %(product_id)s, %(quantity)s)
                    """
                    cur.execute(insert_statement, {"order_id": order_id, "product_id": product_id, "quantity": product["quantity"]})

        conn.commit()


def main():
    conn = psycopg2.connect(
        "host=localhost dbname=postgres user=postgres password=postgres"
    )
    cur = conn.cursor()

    process(cur, conn, filepath="../data")

    conn.close()


if __name__ == "__main__":
    main()