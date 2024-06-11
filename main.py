import os
import pandas as pd
from datetime import datetime
from trading_framework import TradingFramework
from backtesting_framework import BacktestingFramework
from strategies.strategy1 import BollingerKeltnerChaikinSMAStrategy
from strategies.strategy2 import Strategy2
from data_ingestion import fetch_stock_data, save_to_csv, process_data
import config

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

def save_backtesting_results(performance, trade_history, metrics, data_with_signals, filename):
    # Combine all data into a single DataFrame
    combined_df = pd.concat([
        performance.assign(Type='Performance').reset_index(),
        trade_history.assign(Type='Trade History').reset_index(drop=True),
        pd.DataFrame(metrics.items(), columns=['Metric', 'Value']).assign(Type='Metrics', Date=''),
        data_with_signals.assign(Type='Data with Signals').reset_index()
    ], axis=1)
    
    # Save combined DataFrame to CSV
    combined_df.to_csv(filename, index=False)
    print(f"Backtesting results saved to {filename}")

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
    trading_framework = TradingFramework()
    trading_framework.add_strategy(strategy_name, strategies[strategy_name]())
    buy_signals, sell_signals = trading_framework.run_strategy(strategy_name, data)

    # Add signals to data
    data['buy_signal'] = buy_signals
    data['sell_signal'] = sell_signals

    # Initialize backtesting framework and apply signals
    backtesting_framework = BacktestingFramework(
        config.initial_balance,
        config.position_size,
        config.stop_loss,
        config.profit_target1,
        config.partial_sell1,
        config.profit_target2,
        config.partial_sell2,
        config.days_threshold,
        config.price_threshold
    )
    backtesting_framework.apply_signals(data, buy_signals, sell_signals)

    # Output performance
    performance = backtesting_framework.get_performance()
    trade_history = backtesting_framework.get_trade_history()
    metrics = backtesting_framework.calculate_metrics()

    # Save results to CSV
    results_dir = "backtesting_results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    results_filename = os.path.join(results_dir, f"{ticker}_{strategy_name}backtesting_results_.csv")
    save_backtesting_results(performance, trade_history, metrics, data, results_filename)

    print("Backtesting complete.")
    print("Performance Summary:")
    print(performance)
    print("Trade History:")
    print(trade_history)
    print("Metrics:")
    for metric, value in metrics.items():
        print(f"{metric}: {value:.2%}")

if __name__ == "__main__":
    main()
