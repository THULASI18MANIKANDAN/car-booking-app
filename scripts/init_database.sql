-- Initialize the Car Booking Database
-- This script creates all necessary tables and initial data

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create cars table
CREATE TABLE IF NOT EXISTS cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL,
    price_per_day REAL NOT NULL,
    image_url TEXT,
    status TEXT DEFAULT 'available',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create bookings table
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    car_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_amount REAL NOT NULL,
    payment_id TEXT,
    status TEXT DEFAULT 'confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (car_id) REFERENCES cars (id)
);

-- Insert admin user (password: admin123)
INSERT OR IGNORE INTO users (username, email, password, role)
VALUES ('admin', 'thulasitmk181@gmail.com.com', 'ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d', 'admin');

-- Insert sample cars
INSERT OR IGNORE INTO cars (name, brand, model, year, price_per_day, image_url, status, description) VALUES
('Toyota Camry', 'Toyota', 'Camry', 2023, 5000.0, 'https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?w=500', 'available', 'Comfortable sedan perfect for city drives'),
('Honda Civic', 'Honda', 'Civic', 2022, 4500.0, 'https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=500', 'available', 'Reliable and fuel-efficient compact car'),
('BMW X5', 'BMW', 'X5', 2023, 12000.0, 'https://images.unsplash.com/photo-1555215695-3004980ad54e?w=500', 'available', 'Luxury SUV with premium features'),
('Mercedes C-Class', 'Mercedes', 'C-Class', 2023, 10000.0, 'https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=500', 'available', 'Elegant luxury sedan'),
('Ford Mustang', 'Ford', 'Mustang', 2022, 8000.0, 'https://images.unsplash.com/photo-1584345604476-8ec5e12e42dd?w=500', 'available', 'Powerful sports car for thrill seekers'),
('Audi A4', 'Audi', 'A4', 2023, 90000.0, 'https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?w=500', 'available', 'Premium sedan with advanced technology'),
('Volkswagen Golf', 'Volkswagen', 'Golf', 2022, 5000, 'https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=500', 'available', 'Compact hatchback perfect for urban driving'),
('Chevrolet Malibu', 'Chevrolet', 'Malibu', 2023, 5500, 'https://images.unsplash.com/photo-1583121274602-3e2820c69888?w=500', 'available', 'Spacious midsize sedan with modern features');

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_cars_status ON cars(status);
CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_car_id ON bookings(car_id);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
