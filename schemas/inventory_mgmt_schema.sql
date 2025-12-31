-- schemas/inventory_mgmt_schema.sql

-- Current Inventory
CREATE TABLE IF NOT EXISTS inventory (
    inventory_id SERIAL PRIMARY KEY,
    product_id VARCHAR(20) NOT NULL,
    location_id VARCHAR(20),
    quantity INT NOT NULL,
    reorder_level INT,
    reorder_quantity INT,
    last_restocked TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders Table
CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(20) PRIMARY KEY,
    supplier_id VARCHAR(20),
    order_date TIMESTAMP,
    expected_delivery_date DATE,
    status VARCHAR(20),
    total_amount DECIMAL(12,2)
);

-- Order Items
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id VARCHAR(20),
    product_id VARCHAR(20),
    quantity INT,
    unit_price DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);