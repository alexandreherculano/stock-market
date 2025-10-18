{{
    config(
        materialized='table',
        schema='gold'
    )
}}

SELECT
    ticker_symbol,
    -- Group by the first day of the month
    DATE_TRUNC('month', trade_date)::DATE AS trading_month,
    
    -- Aggregated Metrics
    SUM(volume) AS total_monthly_volume,
    CAST(AVG(close_price) AS NUMERIC(10,2))AS avg_monthly_close,
    
    -- Average volatility derived from the fact table
    CAST(AVG(trading_range) AS NUMERIC(10,2)) AS avg_daily_volatility,
    
    -- Count of trading days in the month
    COUNT(price_sk) AS trading_days_count

FROM 
    {{ ref('fact_daily_stock_performance') }} -- Reference the first Gold model (Fact)
    
GROUP BY 
    1, 2
ORDER BY 
    ticker_symbol, trading_month