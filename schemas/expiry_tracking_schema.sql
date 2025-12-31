-- schemas/expiry_tracking_schema.sql

-- Batch Information
CREATE TABLE IF NOT EXISTS batches (
    batch_id VARCHAR(30) PRIMARY KEY,
    product_id VARCHAR(20),
    manufacturing_date DATE,
    expiry_date DATE,
    quantity INT,
    received_date TIMESTAMP,
    location_id VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active'
);

-- Expiry Alerts
CREATE TABLE IF NOT EXISTS expiry_alerts (
    alert_id SERIAL PRIMARY KEY,
    batch_id VARCHAR(30),
    product_id VARCHAR(20),
    days_until_expiry INT,
    alert_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged BOOLEAN DEFAULT FALSE
);