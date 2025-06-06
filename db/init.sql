-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  stripe_customer_id TEXT,
  created_at TIMESTAMP DEFAULT now()
);

-- API Keys table
CREATE TABLE IF NOT EXISTS api_keys (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  key TEXT UNIQUE NOT NULL,
  plan TEXT CHECK (plan IN ('free', 'pro_monthly', 'pro_annual')) NOT NULL DEFAULT 'free',
  stripe_subscription_id TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT now()
);

-- Addresses table (LINZ schema for autocomplete/verify)
CREATE TABLE IF NOT EXISTS addresses (
  address_id INTEGER PRIMARY KEY,
  source_dataset VARCHAR(20),
  change_id INTEGER,
  full_address_number VARCHAR(100),
  full_road_name VARCHAR(250),
  full_address TEXT NOT NULL,
  territorial_authority VARCHAR(80),
  unit_type VARCHAR(100),
  unit_value VARCHAR(70),
  level_type VARCHAR(100),
  level_value VARCHAR(70),
  address_number_prefix VARCHAR(26),
  address_number INTEGER,
  address_number_suffix VARCHAR(10),
  address_number_high INTEGER,
  road_name_prefix VARCHAR(100),
  road_name VARCHAR(100),
  road_type_name VARCHAR(100),
  road_suffix VARCHAR(100),
  water_name VARCHAR(100),
  water_body_name VARCHAR(100),
  suburb_locality TEXT,
  town_city TEXT,
  postcode TEXT,
  address_class VARCHAR(20),
  address_lifecycle VARCHAR(20),
  gd2000_xcoord NUMERIC(20, 8),
  gd2000_ycoord NUMERIC(20, 8),
  location GEOMETRY(POINT, 4167)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_trgm_full_address ON addresses USING GIN (full_address gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_geom_address ON addresses USING GIST (location);
