-- ============================================================
-- Inventory Tracker - Database Schema (PostgreSQL)
-- AICTE Summer Internship Project
-- ============================================================

-- Drop tables if they already exist (useful while testing)
DROP TABLE IF EXISTS inventory_transactions;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS suppliers;
DROP TABLE IF EXISTS categories;

-- ------------------------------------------------------------
-- 1. Categories: groups products (e.g. Electronics, Stationery)
-- ------------------------------------------------------------
CREATE TABLE categories (
    category_id     SERIAL PRIMARY KEY,
    category_name   VARCHAR(50) NOT NULL UNIQUE
);

-- ------------------------------------------------------------
-- 2. Suppliers: vendors who supply products
-- ------------------------------------------------------------
CREATE TABLE suppliers (
    supplier_id     SERIAL PRIMARY KEY,
    supplier_name   VARCHAR(100) NOT NULL,
    contact_email   VARCHAR(100),
    contact_phone   VARCHAR(20)
);

-- ------------------------------------------------------------
-- 3. Products: the items being tracked in inventory
-- ------------------------------------------------------------
CREATE TABLE products (
    product_id      SERIAL PRIMARY KEY,
    product_name    VARCHAR(100) NOT NULL,
    category_id     INTEGER REFERENCES categories(category_id),
    supplier_id     INTEGER REFERENCES suppliers(supplier_id),
    unit_price      NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    quantity_in_stock INTEGER NOT NULL DEFAULT 0 CHECK (quantity_in_stock >= 0),
    reorder_level   INTEGER NOT NULL DEFAULT 10,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- 4. Inventory Transactions: every stock IN / OUT movement
--    This keeps a full history instead of only current stock.
-- ------------------------------------------------------------
CREATE TABLE inventory_transactions (
    transaction_id      SERIAL PRIMARY KEY,
    product_id          INTEGER NOT NULL REFERENCES products(product_id),
    transaction_type    VARCHAR(10) NOT NULL CHECK (transaction_type IN ('IN', 'OUT')),
    quantity            INTEGER NOT NULL CHECK (quantity > 0),
    transaction_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    remarks             VARCHAR(255)
);

-- ------------------------------------------------------------
-- Indexes for faster lookups on commonly queried columns
-- ------------------------------------------------------------
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_supplier ON products(supplier_id);
CREATE INDEX idx_transactions_product ON inventory_transactions(product_id);
