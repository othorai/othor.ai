-- 05-load-sample-data.sql

-- First, ensure the table is empty to avoid duplicates
TRUNCATE TABLE public.wayne_enterprise;

-- Load the CSV data directly using \copy
\copy public.wayne_enterprise(date, department, product, location, revenue, costs, units_sold, customer_satisfaction, marketing_spend, new_customers, repeat_customers, website_visits) FROM '/sample-data/wayne_enterprise.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ',', NULL 'NULL', ENCODING 'UTF8');

-- Verify the data was loaded correctly
DO $$
DECLARE
    row_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO row_count FROM public.wayne_enterprise;
    RAISE NOTICE 'Successfully loaded % rows into wayne_enterprise table', row_count;
END $$;