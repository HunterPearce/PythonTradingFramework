import os
import pandas as pd
from datetime import datetime
from trading_framework import TradingFramework
from strategies.strategy1 import BollingerKeltnerChaikinSMAStrategy
from strategies.strategy2 import Strategy2
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
    return framework

def run_strategy(framework, strategy_name, data):
    buy_signals, sell_signals = framework.run_strategy(strategy_name, data)
    return buy_signals, sell_signals

def save_signals_to_csv(buy_signals, sell_signals, option, strategy_name):
    signals_dir = os.path.join(os.path.dirname(__file__), 'signals', strategy_name)
    os.makedirs(signals_dir, exist_ok=True)
    filename = os.path.join(signals_dir, f"{option.lower()}_signals.csv")
    
    with open(filename, 'w') as f:
        f.write("Buy Signals:\n")
        buy_signals.to_csv(f)
        f.write("\nSell Signals:\n")
        sell_signals.to_csv(f)
    
    print(f"Signals saved to {filename}")

def print_signals(data, buy_signals, sell_signals):
    print("Buy signals:")
    print(data.loc[buy_signals.index, 'Close'])
    print("Sell signals:")
    print(data.loc[sell_signals.index, 'Close'])

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
    strategies = {
        'BollingerKeltnerChaikinSMAStrategy': BollingerKeltnerChaikinSMAStrategy,
        'Strategy2': Strategy2,
        # Add more strategies here as needed
    }

    strategy_names = list(strategies.keys())

    # Get the user's choice of strategy
    strategy_name = get_user_selection(strategy_names, "Please select a strategy by entering the corresponding number:")
    if strategy_name is None:
        return

    # Set date range for data fetching
    start_date = "2020-01-01"
    end_date = datetime.today().strftime('%Y-%m-%d')

    # Process data
    data = process_selected_data(ticker, option, start_date, end_date)
    
    # Initialize framework and run the selected strategy
    framework = initialize_framework()
    framework.add_strategy(strategy_name, strategies[strategy_name]())
    buy_signals, sell_signals = run_strategy(framework, strategy_name, data)
    
    # Save signals to CSV
    save_signals_to_csv(buy_signals, sell_signals, option, strategy_name)

    # Print results
    print_signals(data, buy_signals, sell_signals)

if __name__ == "__main__":
    main()
