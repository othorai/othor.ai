-- 01-schemas.sql

-- First, ensure we're in a clean transaction state
DO $$ 
BEGIN
    -- Check if we can create extensions
    IF NOT EXISTS (
        SELECT 1 FROM pg_available_extensions WHERE name = 'uuid-ossp'
    ) THEN
        RAISE NOTICE 'uuid-ossp extension is not available in the database';
    END IF;
END $$;

-- Create the public schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS public;

-- We need to enable the PostgreSQL extensions we'll be using
-- The uuid-ossp extension must be created in each database explicitly
CREATE EXTENSION IF NOT EXISTS "uuid-ossp" SCHEMA public;
CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- Also useful for cryptographic functions

-- Verify the extension was created successfully
DO $$
BEGIN
    -- Try to generate a UUID to verify the extension works
    PERFORM uuid_generate_v4();
    RAISE NOTICE 'uuid-ossp extension is working correctly';
EXCEPTION WHEN OTHERS THEN
    RAISE EXCEPTION 'Failed to generate UUID. Error: %', SQLERRM;
END $$;


-- Next, let's configure our schema settings
SET search_path TO public;

-- Create our configuration table
CREATE TABLE IF NOT EXISTS public.app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Function for updating timestamps
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to ensure one admin remains
CREATE OR REPLACE FUNCTION public.ensure_one_admin()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'DELETE' OR NEW.role <> 'admin') AND 
       OLD.role = 'admin' AND
       (SELECT COUNT(*) FROM public.user_organizations 
        WHERE organization_id = OLD.organization_id 
        AND role = 'admin') <= 1 THEN
        RAISE EXCEPTION 'Cannot remove the last admin';
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to get application setting
CREATE OR REPLACE FUNCTION public.get_setting(setting_key TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN (SELECT value FROM public.app_settings WHERE key = setting_key);
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ language 'plpgsql';

-- Verify UUID extension is working
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_extension 
        WHERE extname = 'uuid-ossp'
    ) THEN
        RAISE EXCEPTION 'uuid-ossp extension was not properly created';
    END IF;
END $$;