class TradingFramework:
    def __init__(self):
        self.strategies = {}

    def add_strategy(self, name, strategy):
        self.strategies[name] = strategy

    def remove_strategy(self, name):
        if name in self.strategies:
            del self.strategies[name]

    def run_strategy(self, name, data):
        if name in self.strategies:
            return self.strategies[name].execute(data)
        else:
            raise ValueError(f"Strategy {name} not found.")

    def list_strategies(self):
        return list(self.strategies.keys())
