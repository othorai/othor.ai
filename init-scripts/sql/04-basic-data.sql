-- 04-basic-data.sql

-- Create a temporary function to hash the password
CREATE OR REPLACE FUNCTION hash_password(raw_password TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN crypt(raw_password, gen_salt('bf', 12));
END;
$$ LANGUAGE plpgsql;

-- Create default admin user
INSERT INTO public.users (
    email,
    hashed_password,
    is_active,
    is_admin,
    username,
    role,
    data_access,
    is_verified
) VALUES (
    'admin@example.com',
    hash_password('admin123'),
    true,
    true,
    'admin',
    'full',
    'admin',
    true
) ON CONFLICT (email) DO NOTHING;

-- Create demo organization
INSERT INTO public.organizations (
    name,
    is_demo,
    data_source_connected,
    created_by
) VALUES (
    'Demo Organization',
    true,
    true,
    (SELECT id FROM public.users WHERE email = 'admin@example.com')
) ON CONFLICT (name) DO NOTHING;

-- Link admin user to demo organization
INSERT INTO public.user_organizations (
    user_id,
    organization_id,
    role
) VALUES (
    (SELECT id FROM public.users WHERE email = 'admin@example.com'),
    (SELECT id FROM public.organizations WHERE name = 'Demo Organization'),
    'admin'
) ON CONFLICT (user_id, organization_id) DO NOTHING;

-- Create a demo data source connection
INSERT INTO public.data_source_connections (
    id,
    organization_id,
    name,
    source_type,
    connection_params,
    table_name,
    date_column
) VALUES (
    'e89be664-c83d-4661-9e52-a654c0a45d6c',
    (SELECT id FROM public.organizations WHERE name = 'Demo Organization'),
    'Wayne Enterprise Demo Data',
    'postgresql',
    jsonb_build_object(
        'host', COALESCE(current_setting('custom.db_host', true), 'postgres'),
        'port', '5432',
        'database', current_database(),
        'user', COALESCE(current_setting('custom.db_user', true), 'postgres'),
        'password', COALESCE(current_setting('custom.db_password', true), 'postgres')
    ),
    'wayne_enterprise',
    'date'
) ON CONFLICT (id) DO NOTHING;

-- Clear existing data to prevent duplicates
TRUNCATE TABLE wayne_enterprise;

-- Load data using psql's \copy command
\copy wayne_enterprise(date, department, product, location, revenue, costs, units_sold, customer_satisfaction, marketing_spend, new_customers, repeat_customers, website_visits) FROM '/sample-data/wayne_enterprise.csv' WITH CSV HEADER;