{{ config(materialized='table') }}

WITH raw_data AS (
    SELECT * FROM {{ source('public', 'raw_products') }}
)
SELECT
    CAST(product_id AS INTEGER) AS product_id,
    CAST(name AS VARCHAR) AS product_name,
    CAST(category AS VARCHAR) AS category,
    CAST(metadata::json->>'is_active' AS BOOLEAN) AS is_active,
    metadata::json->>'tags' AS product_tags
FROM raw_data