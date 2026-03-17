-- schemas/store_catalog_schema.sql

-- Products Table
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    brand VARCHAR(50),
    barcode VARCHAR(50) UNIQUE,
    base_price DECIMAL(10,2),
    weight_kg DECIMAL(8,3),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Locations Table
CREATE TABLE IF NOT EXISTS locations (
    location_id VARCHAR(20) PRIMARY KEY,
    aisle VARCHAR(10),
    rack VARCHAR(10),
    shelf VARCHAR(10),
    section VARCHAR(50),
    capacity INT
);

-- Suppliers Table
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100),
    contact_email VARCHAR(100),
    contact_phone VARCHAR(30),
    address TEXT,
    reliability_score DECIMAL(3,2),
    average_lead_time_days INT
);

-- Product Location Mapping
CREATE TABLE IF NOT EXISTS product_locations (
    product_id VARCHAR(20),
    location_id VARCHAR(20),
    allocated_space INT,
    PRIMARY KEY (product_id, location_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

-- Product Supplier Mapping
CREATE TABLE IF NOT EXISTS product_suppliers (
    product_id VARCHAR(20),
    supplier_id VARCHAR(20),
    unit_cost DECIMAL(10,2),
    minimum_order_quantity INT,
    PRIMARY KEY (product_id, supplier_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);