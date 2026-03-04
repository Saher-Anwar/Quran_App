-- Initialize database with UTF-8 support for Arabic text with diacritics
-- This script runs automatically when the PostgreSQL container starts

-- Connect to the quran_db database
\c quran_db

-- Ensure the database uses UTF-8 encoding (this is a session parameter)
SET client_encoding TO 'UTF8';

-- Create extension for better text search (optional, useful for Quran search)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create extension for UUID support (useful for primary keys)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant all privileges to admin user on the database
GRANT ALL PRIVILEGES ON DATABASE quran_db TO admin;

-- Grant privileges on the public schema
GRANT ALL ON SCHEMA public TO admin;

-- Set default text search configuration (can be customized for Arabic later)
ALTER DATABASE quran_db SET default_text_search_config TO 'simple';
