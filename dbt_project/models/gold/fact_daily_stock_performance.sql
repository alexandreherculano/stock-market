{{
    config(
        materialized='table',
        schema='gold'
    )
}}

SELECT
    price_sk,
    ticker_symbol,
    trade_date,
    open_price,
    close_price,
    volume,
    
    -- Business Metric 1: Calculate daily return percentage
    ROUND(((close_price - open_price) / open_price) * 100, 4) AS daily_return_pct,

    -- Business Metric 2: Calculate daily trading range (volatility)
    ROUND( (high_price - low_price), 4) AS trading_range
    
FROM 
    {{ ref('stock_prices_alphavantage') }} -- Reference the cleaned Silver model