-- ============================================================
-- Inventory Tracker - Useful Queries, View & Trigger (PostgreSQL)
-- Run this AFTER 01_schema.sql and 02_sample_data.sql
-- ============================================================

-- ------------------------------------------------------------
-- A. BASIC QUERIES
-- ------------------------------------------------------------

-- 1. View all products with category and supplier names
SELECT p.product_id, p.product_name, c.category_name, s.supplier_name,
       p.unit_price, p.quantity_in_stock, p.reorder_level
FROM products p
JOIN categories c ON p.category_id = c.category_id
JOIN suppliers s ON p.supplier_id = s.supplier_id
ORDER BY p.product_id;

-- 2. Products that are low on stock (need reordering)
SELECT product_name, quantity_in_stock, reorder_level
FROM products
WHERE quantity_in_stock <= reorder_level;

-- 3. Total inventory value (price x quantity) per product
SELECT product_name, unit_price, quantity_in_stock,
       (unit_price * quantity_in_stock) AS total_value
FROM products
ORDER BY total_value DESC;

-- 4. Overall inventory value across all products
SELECT SUM(unit_price * quantity_in_stock) AS total_inventory_value
FROM products;

-- 5. Number of products per category
SELECT c.category_name, COUNT(p.product_id) AS total_products
FROM categories c
LEFT JOIN products p ON c.category_id = p.category_id
GROUP BY c.category_name;

-- 6. Products supplied by each supplier
SELECT s.supplier_name, p.product_name
FROM suppliers s
JOIN products p ON s.supplier_id = p.supplier_id
ORDER BY s.supplier_name;

-- 7. Full transaction history for a specific product (example: product_id = 1)
SELECT t.transaction_id, p.product_name, t.transaction_type,
       t.quantity, t.transaction_date, t.remarks
FROM inventory_transactions t
JOIN products p ON t.product_id = p.product_id
WHERE t.product_id = 1
ORDER BY t.transaction_date;

-- 8. Total quantity sold (OUT) per product
SELECT p.product_name, SUM(t.quantity) AS total_sold
FROM inventory_transactions t
JOIN products p ON t.product_id = p.product_id
WHERE t.transaction_type = 'OUT'
GROUP BY p.product_name
ORDER BY total_sold DESC;

-- 9. Most recent 5 transactions across the whole inventory
SELECT t.transaction_id, p.product_name, t.transaction_type,
       t.quantity, t.transaction_date
FROM inventory_transactions t
JOIN products p ON t.product_id = p.product_id
ORDER BY t.transaction_date DESC
LIMIT 5;

-- 10. Search a product by name (partial match, case-insensitive)
SELECT * FROM products
WHERE product_name ILIKE '%chair%';


-- ------------------------------------------------------------
-- B. VIEW: quick current-stock dashboard
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW current_stock_view AS
SELECT p.product_id, p.product_name, c.category_name,
       p.quantity_in_stock, p.reorder_level,
       CASE
           WHEN p.quantity_in_stock <= p.reorder_level THEN 'LOW STOCK'
           ELSE 'OK'
       END AS stock_status
FROM products p
JOIN categories c ON p.category_id = c.category_id;

-- Usage:
-- SELECT * FROM current_stock_view;
-- SELECT * FROM current_stock_view WHERE stock_status = 'LOW STOCK';


-- ------------------------------------------------------------
-- C. TRIGGER: automatically update quantity_in_stock whenever
--    a new transaction (IN/OUT) is recorded
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_stock_on_transaction()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.transaction_type = 'IN' THEN
        UPDATE products
        SET quantity_in_stock = quantity_in_stock + NEW.quantity
        WHERE product_id = NEW.product_id;
    ELSIF NEW.transaction_type = 'OUT' THEN
        UPDATE products
        SET quantity_in_stock = quantity_in_stock - NEW.quantity
        WHERE product_id = NEW.product_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_stock ON inventory_transactions;

CREATE TRIGGER trg_update_stock
AFTER INSERT ON inventory_transactions
FOR EACH ROW
EXECUTE FUNCTION update_stock_on_transaction();

-- NOTE: The sample data in 02_sample_data.sql was inserted directly into
-- products.quantity_in_stock (not through this trigger), so it already
-- reflects the correct final stock. From this point on, any NEW row you
-- insert into inventory_transactions will automatically adjust
-- quantity_in_stock for you. Try it:
--
-- INSERT INTO inventory_transactions (product_id, transaction_type, quantity, remarks)
-- VALUES (1, 'OUT', 5, 'Test trigger - new sale');
--
-- SELECT product_name, quantity_in_stock FROM products WHERE product_id = 1;
