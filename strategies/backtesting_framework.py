import pandas as pd
import numpy as np

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

    def apply_signals(self, data, long_signals, short_signals):
        data['long_signal'] = long_signals
        data['short_signal'] = short_signals

        for index, row in data.iterrows():
            self.apply_trading_rules(row)

    def apply_trading_rules(self, row):
        # Only one trade (either long or short) can be open at a time
        if row['long_signal'] and not self.positions:
            self.enter_long(row)
        elif row['short_signal'] and not self.positions:
            self.enter_short(row)

        self.update_positions(row)
        self.equity_curve.append({'date': row.name, 'balance': self.balance})

    def enter_long(self, row):
        # Calculate position size based on the updated balance
        position_size = self.balance * self.position_size
        quantity = position_size / row['Close']
        stop_loss_price = row['Close'] * (1 - self.stop_loss)
        self.positions.append({
            'type': 'long',
            'entry_price': row['Close'],
            'quantity': quantity,
            'stop_loss': stop_loss_price,
            'date': row.name,
            'target1_reached': False,
            'target2_reached': False
        })
        self.balance -= position_size
        self.trade_history.append({'type': 'long', 'price': row['Close'], 'quantity': quantity, 'date': row.name, 'balance': self.balance})

    def enter_short(self, row):
        # Calculate position size based on the updated balance
        position_size = self.balance * self.position_size
        quantity = position_size / row['Close']
        stop_loss_price = row['Close'] * (1 + self.stop_loss)
        self.positions.append({
            'type': 'short',
            'entry_price': row['Close'],
            'quantity': quantity,
            'stop_loss': stop_loss_price,
            'date': row.name,
            'target1_reached': False,
            'target2_reached': False
        })
        self.balance -= position_size
        self.trade_history.append({'type': 'short', 'price': row['Close'], 'quantity': quantity, 'date': row.name, 'balance': self.balance})

    def update_positions(self, row):
        for position in self.positions.copy():
            if position['type'] == 'long':
                self.check_exit_long(position, row)
            elif position['type'] == 'short':
                self.check_exit_short(position, row)

    def check_exit_long(self, position, row):
        if not position['target1_reached'] and row['Close'] >= position['entry_price'] * self.profit_target1:
            self.partial_exit(position, row, self.partial_sell1)
            position['stop_loss'] = position['entry_price'] * 1.2
            position['target1_reached'] = True
        elif position['target1_reached'] and not position['target2_reached'] and row['Close'] >= position['entry_price'] * self.profit_target2:
            self.partial_exit(position, row, self.partial_sell2)
            position['stop_loss'] = position['entry_price'] * 1.2
            position['target2_reached'] = True
        elif row['Close'] >= position['entry_price'] * 3:
            self.full_exit(position, row)
        elif (row.name - position['date']).days >= self.days_threshold and (row['Close'] - position['entry_price']) / position['entry_price'] <= self.price_threshold:
            self.full_exit(position, row)
        elif row['Close'] < position['stop_loss']:
            self.full_exit(position, row)

    def check_exit_short(self, position, row):
        if not position['target1_reached'] and row['Close'] <= position['entry_price'] * (1 - self.profit_target1):
            self.partial_exit(position, row, self.partial_sell1)
            position['stop_loss'] = position['entry_price'] * 0.8
            position['target1_reached'] = True
        elif position['target1_reached'] and not position['target2_reached'] and row['Close'] <= position['entry_price'] * (1 - self.profit_target2):
            self.partial_exit(position, row, self.partial_sell2)
            position['stop_loss'] = position['entry_price'] * 0.8
            position['target2_reached'] = True
        elif row['Close'] <= position['entry_price'] * 0.5:
            self.full_exit(position, row)
        elif (row.name - position['date']).days >= self.days_threshold and (position['entry_price'] - row['Close']) / position['entry_price'] <= self.price_threshold:
            self.full_exit(position, row)
        elif row['Close'] > position['stop_loss']:
            self.full_exit(position, row)

    def partial_exit(self, position, row, sell_fraction):
        sell_quantity = position['quantity'] * sell_fraction
        self.balance += sell_quantity * row['Close']
        position['quantity'] -= sell_quantity
        self.trade_history.append({'type': 'partial_exit', 'price': row['Close'], 'quantity': sell_quantity, 'date': row.name, 'balance': self.balance})
        if position['quantity'] == 0:
            self.positions.remove(position)

    def full_exit(self, position, row):
        self.balance += position['quantity'] * row['Close']
        self.trade_history.append({'type': 'full_exit', 'price': row['Close'], 'quantity': position['quantity'], 'date': row.name, 'balance': self.balance})
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
        sharpe_ratio = (annualized_return - 0.02) / annualized_volatility
        metrics = {
            'Total Return': total_return,
            'Annualized Return': annualized_return,
            'Annualized Volatility': annualized_volatility,
            'Max Drawdown': max_drawdown,
            'Sharpe Ratio': sharpe_ratio
        }
        return metrics
