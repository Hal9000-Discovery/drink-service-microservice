-- Reset existing tables
DROP TABLE IF EXISTS price;
DROP TABLE IF EXISTS drink;

-- Recreate schema (matches your models)
CREATE TABLE drink (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE price (
    price_id INTEGER PRIMARY KEY AUTOINCREMENT,
    drink_id INTEGER NOT NULL,
    price_amount NUMERIC(10, 2) NOT NULL,
    effective_date DATE NOT NULL,
    end_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (drink_id) REFERENCES drink (id)
);

-- Insert sample drinks
INSERT INTO drink (name, description) VALUES
    ('Latte', 'Espresso with steamed milk'),
    ('Espresso', 'Strong black coffee made by forcing steam through ground coffee beans'),
    ('Cappuccino', 'Espresso with steamed milk and foam'),
    ('Americano', 'Espresso diluted with hot water'),
    ('Mocha', 'Espresso with chocolate and milk'),
    ('Iced Coffee', 'Chilled brewed coffee with ice');

-- Insert sample prices
INSERT INTO price (drink_id, price_amount, effective_date, end_date) VALUES
    (1, 3.75, '2024-11-01', NULL),
    (2, 2.50, '2024-11-01', NULL),
    (3, 4.25, '2024-11-01', NULL),
    (4, 3.00, '2024-11-01', NULL),
    (5, 4.50, '2024-11-01', NULL),
    (6, 3.25, '2024-11-01', NULL);
