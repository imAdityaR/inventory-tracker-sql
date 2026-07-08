"""
inventory.py
Data-access layer: every function opens its own short-lived connection,
runs one parameterized query, and returns plain Python data structures.
Keeping DB access here (separate from cli.py) makes the logic reusable
and easy to unit test later.
"""

from psycopg2 import sql, errors
from app.db import get_connection


# ------------------------------------------------------------------
# READ operations
# ------------------------------------------------------------------

def list_products():
    query = """
        SELECT p.product_id, p.product_name, c.category_name, s.supplier_name,
               p.unit_price, p.quantity_in_stock, p.reorder_level
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        JOIN suppliers s ON p.supplier_id = s.supplier_id
        ORDER BY p.product_id;
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()


def list_categories():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT category_id, category_name FROM categories ORDER BY category_id;")
        return cur.fetchall()


def list_suppliers():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT supplier_id, supplier_name FROM suppliers ORDER BY supplier_id;")
        return cur.fetchall()


def low_stock_report():
    query = """
        SELECT product_name, quantity_in_stock, reorder_level
        FROM products
        WHERE quantity_in_stock <= reorder_level
        ORDER BY quantity_in_stock ASC;
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()


def search_products(keyword: str):
    query = """
        SELECT product_id, product_name, quantity_in_stock, unit_price
        FROM products
        WHERE product_name ILIKE %s
        ORDER BY product_name;
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query, (f"%{keyword}%",))
        return cur.fetchall()


def transaction_history(product_id: int):
    query = """
        SELECT t.transaction_id, t.transaction_type, t.quantity,
               t.transaction_date, t.remarks
        FROM inventory_transactions t
        WHERE t.product_id = %s
        ORDER BY t.transaction_date DESC;
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query, (product_id,))
        return cur.fetchall()


def inventory_value_report():
    query = """
        SELECT product_name, unit_price, quantity_in_stock,
               (unit_price * quantity_in_stock) AS total_value
        FROM products
        ORDER BY total_value DESC;
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        cur.execute("SELECT SUM(unit_price * quantity_in_stock) FROM products;")
        total = cur.fetchone()[0]
        return rows, total


# ------------------------------------------------------------------
# WRITE operations
# ------------------------------------------------------------------

def add_product(name, category_id, supplier_id, unit_price, quantity, reorder_level):
    query = """
        INSERT INTO products
            (product_name, category_id, supplier_id, unit_price, quantity_in_stock, reorder_level)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING product_id;
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query, (name, category_id, supplier_id, unit_price, quantity, reorder_level))
        new_id = cur.fetchone()[0]
        conn.commit()
        return new_id


def record_transaction(product_id: int, transaction_type: str, quantity: int, remarks: str = ""):
    """
    Inserts a stock IN/OUT transaction. The `trg_update_stock` trigger
    (defined in sql/03_queries.sql) automatically keeps
    products.quantity_in_stock in sync -- no manual UPDATE needed here.
    """
    query = """
        INSERT INTO inventory_transactions (product_id, transaction_type, quantity, remarks)
        VALUES (%s, %s, %s, %s);
    """
    with get_connection() as conn, conn.cursor() as cur:
        try:
            cur.execute(query, (product_id, transaction_type.upper(), quantity, remarks))
            conn.commit()
            return True, "Transaction recorded successfully."
        except errors.CheckViolation:
            conn.rollback()
            return False, "Invalid transaction: quantity must be positive and stock cannot go negative."
        except errors.ForeignKeyViolation:
            conn.rollback()
            return False, "Invalid product_id: no such product exists."


def add_category(name: str):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO categories (category_name) VALUES (%s) RETURNING category_id;",
            (name,),
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        return new_id


def add_supplier(name: str, email: str, phone: str):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO suppliers (supplier_name, contact_email, contact_phone)
               VALUES (%s, %s, %s) RETURNING supplier_id;""",
            (name, email, phone),
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
