import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from strategies.Strategy1_Backtesting import Strategy1Backtesting
from strategies.strategy1 import BollingerKeltnerChaikinSMAStrategy
from strategies.strategy2 import Strategy2
from data_ingestion import process_data
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

def save_backtesting_results(performance, trade_history, metrics, filename):
    trade_history_df = pd.DataFrame(trade_history)
    metrics_df = pd.DataFrame(list(metrics.items()), columns=['Metric', 'Value'])
    metrics_df['date'] = None
    combined_df = pd.concat([trade_history_df, metrics_df], axis=0, ignore_index=True)
    combined_df.to_csv(filename, index=False)
    print(f"Backtesting results saved to {filename}")

def plot_equity_curve(trade_history):
    plt.figure(figsize=(10, 6))
    plt.plot(trade_history['date'], trade_history['balance'], label='Equity')
    plt.axhline(100000, color='green', linestyle='--', label=f'Starting Balance: {100000}')
    z = np.polyfit(pd.to_numeric(trade_history['date']), trade_history['balance'], 1)
    p = np.poly1d(z)
    plt.plot(trade_history['date'], p(pd.to_numeric(trade_history['date'])), color='blue', linestyle='--', label='Trend Line')
    plt.title('Equity Curve')
    plt.xlabel('Date')
    plt.ylabel('Equity')
    plt.xlim([datetime(2020, 1, 1), datetime(2024, 12, 31)])
    plt.ylim([90000, 110000])
    plt.legend()
    plt.show()

def plot_drawdown(trade_history):
    running_max = trade_history['balance'].cummax()
    drawdown = trade_history['balance'] / running_max - 1
    
    plt.figure(figsize=(10, 6))
    plt.plot(trade_history['date'], drawdown, label='Drawdown')

    # Adding a horizontal line at 0
    plt.axhline(0, color='green', linestyle='--', label='Zero Line')
    
    # Adding a trend line
    z = np.polyfit(pd.to_numeric(trade_history['date']), drawdown, 1)
    p = np.poly1d(z)
    plt.plot(trade_history['date'], p(pd.to_numeric(trade_history['date'])), color='blue', linestyle='--', label='Trend Line')
    
    plt.title('Drawdown')
    plt.xlabel('Date')
    plt.ylabel('Drawdown')
    plt.xlim([datetime(2018, 1, 1), datetime(2024, 12, 31)])
    plt.ylim([drawdown.min() * 1.3, 0.03]) 
    plt.legend()
    plt.show()


def main():
    options = load_list_from_file('./stocks/options.txt')
    tickers = load_list_from_file('./stocks/tickers.txt')

    ticker = get_user_selection(tickers, "Please select a stock or forex option by entering the corresponding number:")
    if ticker is None:
        return
    option = options[tickers.index(ticker)]

    strategies = {
        'BollingerKeltnerChaikinSMAStrategy': BollingerKeltnerChaikinSMAStrategy,
        'Strategy2': Strategy2,
    }
    backtesting_frameworks = {
        'Strategy1Backtesting': Strategy1Backtesting,
    }

    strategy_name = get_user_selection(list(strategies.keys()), "Please select a strategy by entering the corresponding number:")
    if strategy_name is None:
        return

    backtesting_framework_name = get_user_selection(list(backtesting_frameworks.keys()), "Please select a backtesting framework by entering the corresponding number:")
    if backtesting_framework_name is None:
        return

    start_date = "2018-01-01"
    end_date = "2024-12-31"

    data = process_selected_data(ticker, option, start_date, end_date)

    backtesting = backtesting_frameworks[backtesting_framework_name]
    backtesting_framework = backtesting(
        config.initial_balance,
        config.position_size,
        config.stop_loss,
        config.profit_target1,
        config.partial_sell1,
        config.profit_target2,
        config.partial_sell2,
        config.days_threshold,
        config.price_threshold,
    )

    strategy_instance = strategies[strategy_name]()

    long_signals, short_signals = strategy_instance.execute(data)
    backtesting_framework.apply_signals(data, long_signals, short_signals)

    performance = backtesting_framework.get_performance()
    trade_history = backtesting_framework.get_trade_history()

    last_full_exit_balance = config.initial_balance
    trade_history['profit'] = 0.0

    for i, row in trade_history.iterrows():
        if row['type'] == 'full_exit':
            trade_history.at[i, 'profit'] = row['balance'] - last_full_exit_balance
            last_full_exit_balance = row['balance']

    trade_history = trade_history.to_dict(orient='records')
    
    metrics = backtesting_framework.calculate_metrics()

    results_dir = "backtesting_results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    results_filename = os.path.join(results_dir, f"{ticker}_{strategy_name}_{backtesting_framework_name}_backtesting_results.csv")
    save_backtesting_results(performance, trade_history, metrics, results_filename)

    trade_history_df = pd.DataFrame(trade_history)

    print("Backtesting complete.")
    print("Performance Summary:")
    print(performance)
    print("Trade History:")
    print(trade_history_df)
    print("Metrics:")
    for metric, value in metrics.items():
        if metric in ['Total Return', 'Annualized Return', 'Annualized Volatility', 'Max Drawdown']:
            print(f"{metric}: {value * 100:.2f}%")
        else:
            print(f"{metric}: {value:.2f}")

    plot_equity_curve(trade_history_df)
    plot_drawdown(trade_history_df)

if __name__ == "__main__":
    main()
