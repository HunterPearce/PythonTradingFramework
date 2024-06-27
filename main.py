import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from backtesting import Backtest
from data_ingestion import process_data
import config
from strategies.strategy1 import BollingerKeltnerChaikinSMAStrategy
from strategies.strategy2 import LongOnlyBollingerKeltnerChaikinSMAStrategy

def load_list_from_file(filename):
    # Load options or tickers from a file
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

def display_options(options, prompt):
    # Display a list of options for the user to choose from
    print(prompt)
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

def get_user_choice(num_options):
    # Get the user's choice from the displayed options
    choice = int(input("Enter the number of your choice: ")) - 1
    if choice < 0 or choice >= num_options:
        print("Invalid choice. Please run the program again.")
        return None
    return choice

def get_user_selection(options, prompt):
    # Display options and get the user's selection
    display_options(options, prompt)
    choice = get_user_choice(len(options))
    if choice is None:
        return None
    return options[choice]

def process_selected_data(ticker, option, start_date, end_date):
    # Fetch and process data for the selected ticker and option
    filename = process_data(ticker, option, start_date, end_date)
    data = pd.read_csv(filename, index_col='Date', parse_dates=True)
    return data

def save_backtesting_results(performance, trade_history, metrics, filename):
    # Save backtesting results to a CSV file
    trade_history_df = pd.DataFrame(trade_history)
    metrics_df = pd.DataFrame(list(metrics.items()), columns=['Metric', 'Value'])
    metrics_df['date'] = None
    combined_df = pd.concat([trade_history_df, metrics_df], axis=0, ignore_index=True)
    combined_df.to_csv(filename, index=False)
    print(f"Backtesting results saved to {filename}")

def plot_equity_curve(performance):
    # Plot the equity curve of the strategy
    plt.figure(figsize=(10, 6))
    plt.plot(performance.index, performance['Equity'], label='Equity')
    plt.axhline(100000, color='green', linestyle='--', label=f'Starting Balance: {100000}')
    z = np.polyfit(performance.index.astype(int), performance['Equity'], 1)
    p = np.poly1d(z)
    plt.plot(performance.index, p(performance.index.astype(int)), color='blue', linestyle='--', label='Trend Line')
    plt.title('Equity Curve')
    plt.xlabel('Date')
    plt.ylabel('Equity')
    plt.xlim([datetime(2020, 1, 1), datetime(2024, 12, 31)])
    plt.ylim([performance['Equity'].min() * 0.9, performance['Equity'].max() * 1.1])
    plt.legend()
    plt.show()

def plot_drawdown(performance):
    # Plot the drawdown of the strategy
    running_max = performance['Equity'].cummax()
    drawdown = performance['Equity'] / running_max - 1

    plt.figure(figsize=(10, 6))
    plt.plot(performance.index, drawdown, label='Drawdown')

    # Adding a horizontal line at 0
    plt.axhline(0, color='green', linestyle='--', label='Zero Line')

    # Adding a trend line
    z = np.polyfit(performance.index.astype(int), drawdown, 1)
    p = np.poly1d(z)
    plt.plot(performance.index, p(performance.index.astype(int)), color='blue', linestyle='--', label='Trend Line')

    plt.title('Drawdown')
    plt.xlabel('Date')
    plt.ylabel('Drawdown')
    plt.xlim([datetime(2018, 1, 1), datetime(2024, 12, 31)])
    plt.ylim([drawdown.min() * 1.3, 0.03])
    plt.legend()
    plt.show()

def main():
    # Load options and tickers from files
    options = load_list_from_file('./stocks/options.txt')
    tickers = load_list_from_file('./stocks/tickers.txt')

    # Get user's ticker selection
    ticker = get_user_selection(tickers, "Please select a stock or forex option by entering the corresponding number:")
    if ticker is None:
        return
    option = options[tickers.index(ticker)]

    # Define available strategies
    strategies = {
        'BollingerKeltnerChaikinSMAStrategy': BollingerKeltnerChaikinSMAStrategy,
        'LongOnlyBollingerKeltnerChaikinSMAStrategy': LongOnlyBollingerKeltnerChaikinSMAStrategy,
    }

    # Get user's strategy selection
    strategy_name = get_user_selection(list(strategies.keys()), "Please select a strategy by entering the corresponding number:")
    if strategy_name is None:
        return

    start_date = "2018-01-01"
    end_date = "2024-12-31"

    # Process data for the selected ticker and option
    data = process_selected_data(ticker, option, start_date, end_date)

    # Set up and run the backtest
    bt = Backtest(data, strategies[strategy_name], cash=config.initial_balance, commission=config.commission, exclusive_orders=True)
    output = bt.run()
    bt.plot()

    # Get the performance and trade history
    performance = output['_equity_curve']
    trade_history = output['_trades']

    # Save backtesting results
    results_dir = "backtesting_results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    results_filename = os.path.join(results_dir, f"{ticker}_{strategy_name}_backtesting_results.csv")
    save_backtesting_results(performance, trade_history, output, results_filename)

    # Print summary and results
    print("Backtesting complete.")
    print("Performance Summary:")
    print(performance)
    print("Trade History:")
    print(trade_history)
    print("Metrics:")
    for metric, value in output.items():
        if isinstance(value, (pd.Timedelta, np.timedelta64)):
            print(f"{metric}: {value}")
        elif isinstance(value, (int, float)):
            print(f"{metric}: {value:.2f}")
        else:
            print(f"{metric}: {value}")

    # Plot the equity curve and drawdown
    plot_equity_curve(performance)
    plot_drawdown(performance)

if __name__ == "__main__":
    main()
