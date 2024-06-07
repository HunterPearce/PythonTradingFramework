import os
import yfinance as yf
import pandas as pd
from datetime import datetime

def fetch_stock_data(ticker, start_date, end_date):
    print(f"Fetching data for {ticker} from {start_date} to {end_date}")
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    print(f"Data fetched: {stock_data.shape[0]} rows")
    return stock_data

def save_to_csv(data, filename):
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist. Creating it.")
        os.makedirs(directory, exist_ok=True)
    else:
        print(f"Directory {directory} already exists.")
    
    print(f"Saving data to {filename}")
    data.to_csv(filename)
    print("Data saved successfully.")

def process_data(ticker, option, start_date, end_date):
    # Set the filename for storing data using the option name
    filename = os.path.join(os.path.dirname(__file__), f"data/{option.lower().replace(' ', '_')}_data.csv")

    # Fetch and save data
    stock_data = fetch_stock_data(ticker, start_date, end_date)
    save_to_csv(stock_data, filename)
    
    return filename

if __name__ == "__main__":
    ticker = input("Enter the stock ticker symbol: ").upper()
    start_date = "2020-01-01"
    end_date = datetime.today().strftime('%Y-%m-%d')
    filename = os.path.join(os.path.dirname(__file__), f"data/{ticker.lower()}_stock_data.csv")

    stock_data = fetch_stock_data(ticker, start_date, end_date)
    save_to_csv(stock_data, filename)
    print(f"Data for {ticker} saved to {filename}")
