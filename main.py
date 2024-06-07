import os
import pandas as pd
from datetime import datetime
from framework import TradingFramework
from strategies.example_strategy import ExampleStrategy
from data_ingestion import process_data

def load_list_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

def main():
    # Load options and tickers from text files
    options = load_list_from_file('./stocks/options.txt')
    tickers = load_list_from_file('./stocks/tickers.txt')

    # Display the options to the user
    print("Please select a stock or forex option by entering the corresponding number:")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

    # Get the user's choice
    choice = int(input("Enter the number of your choice: ")) - 1

    # Validate choice
    if choice < 0 or choice >= len(tickers):
        print("Invalid choice. Please run the program again.")
        return

    # Get the corresponding ticker and option name
    ticker = tickers[choice]
    option = options[choice]

    # Set date range for data fetching
    start_date = "2020-01-01"
    end_date = datetime.today().strftime('%Y-%m-%d')

    # Process data in data_ingestion.py
    filename = process_data(ticker, option, start_date, end_date)

    # Read data from the CSV file
    data = pd.read_csv(filename, index_col='Date', parse_dates=True)
    
    # Initialize and add strategies to the framework
    framework = TradingFramework()
    example_strategy = ExampleStrategy()
    framework.add_strategy('ExampleStrategy', example_strategy)

    # Run a strategy
    buy_signals, sell_signals = framework.run_strategy('ExampleStrategy', data)
    
    # Print results
    print("Buy signals:")
    print(data.loc[buy_signals, 'Close'])
    print("Sell signals:")
    print(data.loc[sell_signals, 'Close'])

if __name__ == "__main__":
    main()
