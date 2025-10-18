{{
    config(
        materialized='table',
        schema='silver'
    )
}}

WITH source_data AS (
    SELECT
        -- Creates a synthetic key (SK) to be used as the Primary Key
        MD5(CAST("ticker" AS TEXT) || CAST("date" AS TEXT)) AS price_sk,

        -- Standardization and Cleaning
        UPPER("ticker") AS ticker_symbol,
        
        -- Difining data types explicitly
        CAST("date" AS DATE) AS trade_date,
        CAST("open" AS NUMERIC(10,2)) AS open_price,
        CAST("high" AS NUMERIC(10,2)) AS high_price,
        CAST("low" AS NUMERIC(10,2)) AS low_price,
        CAST("close" AS NUMERIC(10,2)) AS close_price,
        CAST("volume" AS BIGINT) AS volume
    
    FROM 

        {{ source('bronze_alpha_vantage', 'stock_prices_alphavantage') }} 
)

-- Apply filters to ensure data quality
SELECT
    *
FROM 
    source_data
WHERE 
    open_price IS NOT NULL
    AND close_price IS NOT NULL
    AND volume >= 0