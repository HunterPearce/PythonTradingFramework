import pandas as pd
import numpy as np
import config

class BacktestingFramework:
    def __init__(self, initial_balance, position_size, stop_loss, profit_target1, partial_sell1, profit_target2, partial_sell2, days_threshold, price_threshold):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position_size = position_size
        self.stop_loss = stop_loss
        self.profit_target1 = profit_target1
        self.partial_sell1 = partial_sell1
        self.profit_target2 = profit_target2
        self.partial_sell2 = partial_sell2
        self.days_threshold = days_threshold
        self.price_threshold = price_threshold
        self.positions = []
        self.trade_history = []
        self.equity_curve = []

    def apply_signals(self, data, buy_signals, sell_signals):
        data['buy_signal'] = buy_signals
        data['sell_signal'] = sell_signals

        for index, row in data.iterrows():
            self.apply_trading_rules(row)

    def apply_trading_rules(self, row):
        if row['buy_signal']:
            self.enter_long(row)
        elif row['sell_signal']:
            self.enter_short(row)

        self.update_positions(row)
        self.equity_curve.append({'date': row.name, 'balance': self.balance})

    def enter_long(self, row):
        position_size = self.balance * self.position_size
        quantity = position_size / row['Close']
        stop_loss_price = row['Close'] * (1 - self.stop_loss)
        self.positions.append({'type': 'long', 'entry_price': row['Close'], 'quantity': quantity, 'stop_loss': stop_loss_price, 'date': row.name})
        self.balance -= position_size
        self.trade_history.append({'type': 'buy', 'price': row['Close'], 'quantity': quantity, 'date': row.name})

    def enter_short(self, row):
        position_size = self.balance * self.position_size
        quantity = position_size / row['Close']
        stop_loss_price = row['Close'] * (1 + self.stop_loss)
        self.positions.append({'type': 'short', 'entry_price': row['Close'], 'quantity': quantity, 'stop_loss': stop_loss_price, 'date': row.name})
        self.balance -= position_size
        self.trade_history.append({'type': 'sell', 'price': row['Close'], 'quantity': quantity, 'date': row.name})

    def update_positions(self, row):
        for position in self.positions:
            if position['type'] == 'long':
                self.check_exit_long(position, row)
            elif position['type'] == 'short':
                self.check_exit_short(position, row)

    def check_exit_long(self, position, row):
        if row['Close'] >= position['entry_price'] * self.profit_target1:
            self.partial_sell(position, row, self.partial_sell1)
            position['stop_loss'] = position['entry_price'] * (1 + 0.2)
        elif row['Close'] >= position['entry_price'] * self.profit_target2:
            self.partial_sell(position, row, self.partial_sell2)
            position['stop_loss'] = position['entry_price'] * (1 + 0.2)
        elif row['Close'] < position['stop_loss']:
            self.sell(position, row)
        elif (row.name - position['date']).days >= self.days_threshold and (row['Close'] - position['entry_price']) / position['entry_price'] <= self.price_threshold:
            self.sell(position, row)

    def check_exit_short(self, position, row):
        if row['Close'] <= position['entry_price'] * self.profit_target1:
            self.partial_sell(position, row, self.partial_sell1)
            position['stop_loss'] = position['entry_price'] * (1 - 0.2)
        elif row['Close'] <= position['entry_price'] * self.profit_target2:
            self.partial_sell(position, row, self.partial_sell2)
            position['stop_loss'] = position['entry_price'] * (1 - 0.2)
        elif row['Close'] > position['stop_loss']:
            self.buy(position, row)
        elif (row.name - position['date']).days >= self.days_threshold and (position['entry_price'] - row['Close']) / position['entry_price'] <= self.price_threshold:
            self.buy(position, row)

    def partial_sell(self, position, row, sell_fraction):
        sell_quantity = position['quantity'] * sell_fraction
        self.balance += sell_quantity * row['Close']
        position['quantity'] -= sell_quantity
        self.trade_history.append({'type': 'partial_sell', 'price': row['Close'], 'quantity': sell_quantity, 'date': row.name})

    def sell(self, position, row):
        self.balance += position['quantity'] * row['Close']
        self.trade_history.append({'type': 'sell', 'price': row['Close'], 'quantity': position['quantity'], 'date': row.name})
        self.positions.remove(position)

    def buy(self, position, row):
        self.balance += position['quantity'] * row['Close']
        self.trade_history.append({'type': 'buy', 'price': row['Close'], 'quantity': position['quantity'], 'date': row.name})
        self.positions.remove(position)

    def get_performance(self):
        return pd.DataFrame(self.equity_curve).set_index('date')

    def get_trade_history(self):
        return pd.DataFrame(self.trade_history)

    def calculate_metrics(self):
        df = pd.DataFrame(self.equity_curve).set_index('date')
        df['returns'] = df['balance'].pct_change().fillna(0)

        total_return = (df['balance'].iloc[-1] - self.initial_balance) / self.initial_balance
        annualized_return = (1 + total_return) ** (365 / len(df)) - 1

        daily_volatility = df['returns'].std()
        annualized_volatility = daily_volatility * np.sqrt(252)

        max_drawdown = (df['balance'] / df['balance'].cummax() - 1).min()

        sharpe_ratio = (annualized_return - 0.02) / annualized_volatility  # Assuming risk-free rate of 2%

        metrics = {
            'Total Return': total_return,
            'Annualized Return': annualized_return,
            'Annualized Volatility': annualized_volatility,
            'Max Drawdown': max_drawdown,
            'Sharpe Ratio': sharpe_ratio
        }

        return metrics

