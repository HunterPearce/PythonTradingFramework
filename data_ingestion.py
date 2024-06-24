import os
import yfinance as yf
import pandas as pd

def fetch_stock_data(ticker, start_date, end_date):
    print(f"Fetching data for {ticker} from {start_date} to {end_date}")
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    print(f"Data fetched: {stock_data.shape[0]} rows")
    return stock_data

def save_to_csv(data, filename):
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    data.to_csv(filename)
    print("Data saved successfully.")

def process_data(ticker, option, start_date, end_date):
    filename = os.path.join(os.path.dirname(__file__), f"data/{option.lower().replace(' ', '_')}_data.csv")
    stock_data = fetch_stock_data(ticker, start_date, end_date)
    save_to_csv(stock_data, filename)
    return filename
