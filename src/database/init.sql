-- Initialize demo database

-- Create additional tables if needed
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert additional sample data
INSERT INTO orders (user_id, product_id, quantity, total_price, status) 
VALUES 
(1, 1, 1, 999.99, 'completed'),
(2, 2, 2, 59.98, 'completed')
ON CONFLICT (id) DO NOTHING;