import os
import time
from datetime import datetime, timedelta

import pandas as pd
import requests
from sqlalchemy import create_engine, text # Added 'text' import for bronze SQL


# EXTRACTION AND DATABASE CONFIGURATION

TICKERS = ['MSFT', 'AAPL', 'NVDA', 'GOOGL', 'AMZN']
FUNCTION = "TIME_SERIES_DAILY"
INTERVAL = "DAILY"

# Database variables
DB_HOST = "postgres" 
DB_USER = "airflow"
DB_PASS = "airflow"
DB_NAME = "airflow"
SCHEMA_NAME = "bronze"
TABLE_NAME = "stock_prices_alphavantage"

def run_extraction_pipeline():
    """Extracts data from Alpha Vantage and loads it into PostgreSQL."""
    
    # 1. Get API Key from Airflow Environment Variables
    API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")
    if not API_KEY:
        # In a real Airflow environment, this variable must be set
        raise ValueError("ALPHA_VANTAGE_API_KEY is not configured.")

    # 2. Database Connection Configuration
    try:
        db_connection_url = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
        engine = create_engine(db_connection_url)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise e

    df_shape = pd.DataFrame()
    d1_str = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    print(f"Starting extraction for date: {d1_str}")
    
    # 3. API Extraction Loop
    for ticker in TICKERS:
        url = (
            f'https://www.alphavantage.co/query?function={FUNCTION}&symbol={ticker}'
            f'&interval={INTERVAL}&apikey={API_KEY}'
        )
        print(f"Requesting data for ticker: {ticker}")
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status() 
            data = r.json()

            time_series_data = data.get("Time Series (Daily)", {})
            
            if d1_str in time_series_data:
                time_series_d1 = time_series_data[d1_str]
                
                # Convert data to DataFrame
                df_response = pd.DataFrame.from_dict(time_series_d1, orient='index').T
                
                # Clean columns and add metadata
                df_response.columns = [str(col).split('. ')[-1] for col in df_response.columns]
                df_response['ticker'] = ticker
                df_response['date'] = d1_str

                df_shape = pd.concat([df_shape, df_response], ignore_index=True)
            else:
                print(f"Warning: No data available for {ticker} on {d1_str}.")

        except requests.exceptions.RequestException as req_err:
            print(f"Request error for {ticker}: {req_err}")
            
        # Alpha Vantage free API rate limit (5 calls per minute)
        time.sleep(12) 

    # 4. PostgreSQL Loading (Load)
    if not df_shape.empty:
        print(f"Data successfully extracted. Rows to load: {len(df_shape)}")
        try:
            # FIX: Use engine.begin() for DDL operations (like CREATE SCHEMA).
            # This automatically manages the transaction and commits it, resolving the 'commit' error.
            with engine.begin() as conn:
                conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}"))

            # Insert data using pandas to_sql (This is auto-committed by pandas' underlying connection logic)
            df_shape.to_sql(
                TABLE_NAME, 
                engine, 
                schema=SCHEMA_NAME, 
                if_exists='append', 
                index=False
            )
            print(f"Data successfully loaded into table {SCHEMA_NAME}.{TABLE_NAME}")
        except Exception as e:
            print(f"Error loading data into PostgreSQL: {e}")
            raise e
    else:
        print("No valid data extracted. Task finished.")
