{{ config(materialized='table') }}

WITH daily_sales AS (
    SELECT
        CAST(order_timestamp AS DATE) AS date_day,
        CAST(product_id AS INTEGER) AS product_id,
        SUM(CAST(quantity AS INTEGER)) AS total_quantity_sold,
        SUM(CAST(total_price AS NUMERIC)) AS total_revenue
    FROM {{ source('public', 'raw_orders') }}
    GROUP BY 1, 2
),
daily_reviews AS (
    SELECT
        CURRENT_DATE AS date_day,
        CAST(product_id AS INTEGER) AS product_id,
        AVG(CAST(rating AS NUMERIC)) AS avg_rating,
        COUNT(review_id) AS review_count
    FROM {{ source('public', 'raw_reviews') }}
    GROUP BY 1, 2
)

SELECT
    COALESCE(s.date_day, r.date_day) AS date_day,
    COALESCE(s.product_id, r.product_id) AS product_id,
    COALESCE(s.total_quantity_sold, 0) AS total_quantity_sold,
    COALESCE(s.total_revenue, 0) AS total_revenue,
    r.avg_rating,
    COALESCE(r.review_count, 0) AS review_count
FROM daily_sales s
FULL OUTER JOIN daily_reviews r
    ON s.product_id = r.product_id AND s.date_day = r.date_day