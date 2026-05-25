{{ config(materialized='table') }}

WITH raw_orders AS (
    SELECT customer_id FROM {{ source('public', 'raw_orders') }}
),
raw_reviews AS (
    SELECT customer_id FROM {{ source('public', 'raw_reviews') }}
)
SELECT DISTINCT CAST(customer_id AS INTEGER) AS customer_id
FROM (
    SELECT customer_id FROM raw_orders
    UNION
    SELECT customer_id FROM raw_reviews
) AS all_customers
WHERE customer_id IS NOT NULL