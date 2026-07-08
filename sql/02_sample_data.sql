-- ============================================================
-- Inventory Tracker - Sample Data (PostgreSQL)
-- Run this AFTER 01_schema.sql
-- ============================================================

-- Categories
INSERT INTO categories (category_name) VALUES
('Electronics'),
('Stationery'),
('Furniture'),
('Groceries');

-- Suppliers
INSERT INTO suppliers (supplier_name, contact_email, contact_phone) VALUES
('TechWorld Distributors', 'sales@techworld.com', '9876543210'),
('OfficeMart Supplies', 'contact@officemart.com', '9123456780'),
('HomeStyle Furnishers', 'info@homestyle.com', '9988776655');

-- Products
INSERT INTO products (product_name, category_id, supplier_id, unit_price, quantity_in_stock, reorder_level) VALUES
('Wireless Mouse', 1, 1, 550.00, 40, 10),
('USB-C Charger', 1, 1, 899.00, 25, 15),
('A4 Notebook', 2, 2, 60.00, 200, 50),
('Ballpoint Pen (Box of 10)', 2, 2, 120.00, 15, 20),
('Office Chair', 3, 3, 4500.00, 8, 5),
('Study Table', 3, 3, 3200.00, 5, 5),
('Basmati Rice (5kg)', 4, 2, 650.00, 30, 10);

-- Inventory Transactions (stock movement history)
INSERT INTO inventory_transactions (product_id, transaction_type, quantity, remarks) VALUES
(1, 'IN', 50, 'Initial stock received'),
(1, 'OUT', 10, 'Sold to customer batch #1'),
(2, 'IN', 30, 'Initial stock received'),
(2, 'OUT', 5, 'Sold to customer batch #2'),
(3, 'IN', 250, 'Initial stock received'),
(3, 'OUT', 50, 'Bulk order - college supply'),
(4, 'IN', 30, 'Initial stock received'),
(4, 'OUT', 15, 'Retail sale'),
(5, 'IN', 10, 'Initial stock received'),
(5, 'OUT', 2, 'Sold to office client'),
(6, 'IN', 5, 'Initial stock received'),
(7, 'IN', 40, 'Initial stock received'),
(7, 'OUT', 10, 'Sold in local store');
