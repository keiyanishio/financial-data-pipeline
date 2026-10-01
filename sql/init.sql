CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;

COMMENT ON SCHEMA raw IS
    'Data ingested from source systems with minimal transformation.';

COMMENT ON SCHEMA staging IS
    'Cleaned, typed and standardized data used as an intermediate layer.';

COMMENT ON SCHEMA analytics IS
    'Business-ready analytical models and data marts.';