from framework import Strategy

class ExampleStrategy(Strategy):
    def execute(self, data):
        # Implement your strategy logic here
        # For example, a simple moving average crossover
        data['SMA50'] = data['Close'].rolling(window=50).mean()
        data['SMA200'] = data['Close'].rolling(window=200).mean()
        
        buy_signals = (data['SMA50'] > data['SMA200']) & (data['SMA50'].shift(1) <= data['SMA200'].shift(1))
        sell_signals = (data['SMA50'] < data['SMA200']) & (data['SMA50'].shift(1) >= data['SMA200'].shift(1))
        
        return buy_signals, sell_signals
