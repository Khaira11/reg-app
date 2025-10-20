-- This file is for manual database initialization if needed
-- The app will automatically create the database and table

CREATE DATABASE IF NOT EXISTS registration_db;

USE registration_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
