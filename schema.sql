-- Car Rental & Return Management System Database Schema
CREATE DATABASE IF NOT EXISTS car_rental_db;
USE car_rental_db;

-- 1. Vehicle Categories
CREATE TABLE IF NOT EXISTS vehicle_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL,
    daily_rate DECIMAL(10,2) NOT NULL
);

-- 2. Branches
CREATE TABLE IF NOT EXISTS branches (
    branch_id INT AUTO_INCREMENT PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL,
    location VARCHAR(150) NOT NULL
);

-- 3. Customers
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL
);

-- 4. Vehicles
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    vin VARCHAR(50) UNIQUE NOT NULL,
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year INT NOT NULL,
    license_plate VARCHAR(20) UNIQUE NOT NULL,
    status ENUM('AVAILABLE', 'RENTED', 'MAINTENANCE') DEFAULT 'AVAILABLE',
    odometer INT NOT NULL,
    category_id INT,
    branch_id INT,
    FOREIGN KEY (category_id) REFERENCES vehicle_categories(category_id) ON DELETE CASCADE,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id) ON DELETE CASCADE
);

-- 5. Rentals
CREATE TABLE IF NOT EXISTS rentals (
    rental_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    vehicle_id INT,
    pickup_date DATETIME NOT NULL,
    expected_return_date DATETIME NOT NULL,
    actual_return_date DATETIME,
    days_rented INT NOT NULL,
    pickup_odometer INT NOT NULL,
    return_odometer INT,
    pickup_fuel DECIMAL(5,2) DEFAULT 100.0,
    status ENUM('ACTIVE', 'RETURNED', 'CANCELLED') DEFAULT 'ACTIVE',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE
);

-- 6. Damages
CREATE TABLE IF NOT EXISTS damages (
    damage_id INT AUTO_INCREMENT PRIMARY KEY,
    rental_id INT,
    description TEXT,
    repair_cost DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (rental_id) REFERENCES rentals(rental_id) ON DELETE CASCADE
);

-- 7. Invoices
CREATE TABLE IF NOT EXISTS invoices (
    invoice_id INT AUTO_INCREMENT PRIMARY KEY,
    rental_id INT,
    base_cost DECIMAL(10,2) NOT NULL,
    damage_fee DECIMAL(10,2) DEFAULT 0.00,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_status ENUM('PAID', 'UNPAID', 'PENDING') DEFAULT 'PAID',
    issue_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rental_id) REFERENCES rentals(rental_id) ON DELETE CASCADE
);

-- Seed Minimal Data
INSERT IGNORE INTO vehicle_categories (category_id, category_name, daily_rate) VALUES (1, 'Sedan', 50.00), (2, 'SUV', 80.00);
INSERT IGNORE INTO branches (branch_id, branch_name, location) VALUES (1, 'Main Branch', 'Downtown');
INSERT IGNORE INTO customers (customer_id, full_name, email, phone) VALUES (1, 'John Doe', 'john@example.com', '555-0199');
