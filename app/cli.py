"""
cli.py
A simple menu-driven command line interface for the Inventory Tracker.
Keeps all input()/print() logic here, separate from the data-access
layer in inventory.py.
"""

from app import inventory


MENU = """
==================================================
   📦  INVENTORY TRACKER
==================================================
 1. View all products
 2. Add a new product
 3. Record stock IN (add stock)
 4. Record stock OUT (remove stock)
 5. Low stock alert
 6. Search product by name
 7. View transaction history for a product
 8. Inventory value report
 9. Add category
10. Add supplier
 0. Exit
==================================================
"""


def print_table(rows, headers):
    if not rows:
        print("  (no records found)\n")
        return
    col_widths = [
        max(len(str(h)), max((len(str(r[i])) for r in rows), default=0))
        for i, h in enumerate(headers)
    ]
    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    print(header_line)
    print("-" * len(header_line))
    for row in rows:
        print(" | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(headers))))
    print()


def view_products():
    rows = inventory.list_products()
    headers = ["ID", "Product", "Category", "Supplier", "Price", "Qty", "Reorder Lvl"]
    print_table(rows, headers)


def add_product():
    print("\n-- Add New Product --")
    categories = inventory.list_categories()
    suppliers = inventory.list_suppliers()

    print("Categories:", ", ".join(f"{c[0]}={c[1]}" for c in categories))
    print("Suppliers :", ", ".join(f"{s[0]}={s[1]}" for s in suppliers))

    try:
        name = input("Product name: ").strip()
        category_id = int(input("Category ID: "))
        supplier_id = int(input("Supplier ID: "))
        price = float(input("Unit price: "))
        qty = int(input("Initial quantity: "))
        reorder = int(input("Reorder level: "))
    except ValueError:
        print("❌ Invalid input. Please enter numbers where expected.\n")
        return

    new_id = inventory.add_product(name, category_id, supplier_id, price, qty, reorder)
    print(f"✅ Product '{name}' added with ID {new_id}.\n")


def stock_movement(transaction_type: str):
    label = "IN (add stock)" if transaction_type == "IN" else "OUT (remove stock)"
    print(f"\n-- Record Stock {label} --")
    try:
        product_id = int(input("Product ID: "))
        qty = int(input("Quantity: "))
    except ValueError:
        print("❌ Invalid input. Product ID and quantity must be numbers.\n")
        return
    remarks = input("Remarks (optional): ").strip()

    success, message = inventory.record_transaction(product_id, transaction_type, qty, remarks)
    print(("✅ " if success else "❌ ") + message + "\n")


def low_stock():
    rows = inventory.low_stock_report()
    headers = ["Product", "Qty in Stock", "Reorder Level"]
    print("\n-- Low Stock Alert --")
    print_table(rows, headers)


def search_products():
    keyword = input("\nEnter product name (or part of it): ").strip()
    rows = inventory.search_products(keyword)
    headers = ["ID", "Product", "Qty", "Price"]
    print_table(rows, headers)


def view_transaction_history():
    try:
        product_id = int(input("\nProduct ID: "))
    except ValueError:
        print("❌ Invalid product ID.\n")
        return
    rows = inventory.transaction_history(product_id)
    headers = ["Txn ID", "Type", "Qty", "Date", "Remarks"]
    print_table(rows, headers)


def value_report():
    rows, total = inventory.inventory_value_report()
    headers = ["Product", "Unit Price", "Qty", "Total Value"]
    print("\n-- Inventory Value Report --")
    print_table(rows, headers)
    print(f"TOTAL INVENTORY VALUE: {total}\n")


def add_category():
    name = input("\nNew category name: ").strip()
    new_id = inventory.add_category(name)
    print(f"✅ Category '{name}' added with ID {new_id}.\n")


def add_supplier():
    print("\n-- Add New Supplier --")
    name = input("Supplier name: ").strip()
    email = input("Contact email: ").strip()
    phone = input("Contact phone: ").strip()
    new_id = inventory.add_supplier(name, email, phone)
    print(f"✅ Supplier '{name}' added with ID {new_id}.\n")


ACTIONS = {
    "1": view_products,
    "2": add_product,
    "3": lambda: stock_movement("IN"),
    "4": lambda: stock_movement("OUT"),
    "5": low_stock,
    "6": search_products,
    "7": view_transaction_history,
    "8": value_report,
    "9": add_category,
    "10": add_supplier,
}


def run():
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye! 👋")
            break
        action = ACTIONS.get(choice)
        if action:
            try:
                action()
            except Exception as e:
                print(f"❌ Something went wrong: {e}\n")
        else:
            print("❌ Invalid option. Please try again.\n")
