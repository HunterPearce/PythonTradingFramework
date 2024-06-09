import os
import pandas as pd
from datetime import datetime
from framework import TradingFramework
from strategies.example_strategy import ExampleStrategy
from data_ingestion import process_data

def load_list_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

def display_options(options, prompt):
    print(prompt)
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

def get_user_choice(num_options):
    choice = int(input("Enter the number of your choice: ")) - 1
    if choice < 0 or choice >= num_options:
        print("Invalid choice. Please run the program again.")
        return None
    return choice

def get_user_selection(options, prompt):
    display_options(options, prompt)
    choice = get_user_choice(len(options))
    if choice is None:
        return None
    return options[choice]

def process_selected_data(ticker, option, start_date, end_date):
    filename = process_data(ticker, option, start_date, end_date)
    data = pd.read_csv(filename, index_col='Date', parse_dates=True)
    return data

def initialize_framework():
    framework = TradingFramework()
    example_strategy = ExampleStrategy()
    framework.add_strategy('ExampleStrategy', example_strategy)
    return framework

def run_strategy(framework, strategy_name, data):
    buy_signals, sell_signals = framework.run_strategy(strategy_name, data)
    return buy_signals, sell_signals

def print_signals(data, buy_signals, sell_signals):
    print("Buy signals:")
    print(data.loc[buy_signals, 'Close'])
    print("Sell signals:")
    print(data.loc[sell_signals, 'Close'])

def main():
    # Load options and tickers from text files
    options = load_list_from_file('./stocks/options.txt')
    tickers = load_list_from_file('./stocks/tickers.txt')

    # Get the user's choice of ticker and option
    ticker = get_user_selection(tickers, "Please select a stock or forex option by entering the corresponding number:")
    if ticker is None:
        return
    option = options[tickers.index(ticker)]

    # Define available strategies
    strategies = ['ExampleStrategy']  # Add more strategies as needed

    # Get the user's choice of strategy
    strategy_name = get_user_selection(strategies, "Please select a strategy by entering the corresponding number:")
    if strategy_name is None:
        return

    # Set date range for data fetching
    start_date = "2020-01-01"
    end_date = datetime.today().strftime('%Y-%m-%d')

    # Process data
    data = process_selected_data(ticker, option, start_date, end_date)
    
    # Initialize framework and run the selected strategy
    framework = initialize_framework()
    buy_signals, sell_signals = run_strategy(framework, strategy_name, data)
    
    # Print results
    print_signals(data, buy_signals, sell_signals)

if __name__ == "__main__":
    main()
