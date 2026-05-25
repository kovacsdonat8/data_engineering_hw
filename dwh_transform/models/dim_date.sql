{{ config(materialized='table') }}

WITH dates AS (
    SELECT DISTINCT CAST(order_timestamp AS DATE) AS date_day
    FROM {{ source('public', 'raw_orders') }}
    WHERE order_timestamp IS NOT NULL
)
SELECT
    date_day,
    EXTRACT(YEAR FROM date_day) AS year,
    EXTRACT(MONTH FROM date_day) AS month,
    EXTRACT(DAY FROM date_day) AS day
FROM dates