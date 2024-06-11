import pandas as pd
import numpy as np
import pandas_ta as ta
from .strategy_base import Strategy

class BollingerKeltnerChaikinSMAStrategy(Strategy):
    """
    Bollinger-Keltner Chaikin SMA Strategy
    --------------------------------------
    This strategy combines Bollinger Bands, Keltner Channels, the Chaikin Oscillator, 
    and a Simple Moving Average (SMA) to generate buy and sell signals.
    
    The strategy buys when the upper Bollinger Band is below the upper Keltner Band, the lower 
    Bollinger Band is above the lower Keltner Band, the Chaikin Oscillator is above 
    zero, and the 100-period SMA is rising. 

    It sells when the opposite conditions are met.
    """

    def __init__(self, position_size=0.02, stop_loss=0.05, profit_target1=2, partial_sell1=0.5, profit_target2=2.5, partial_sell2=0.5, days_threshold=10, price_threshold=0.05):
        self.position_size = position_size
        self.stop_loss = stop_loss
        self.profit_target1 = profit_target1
        self.partial_sell1 = partial_sell1
        self.profit_target2 = profit_target2
        self.partial_sell2 = partial_sell2
        self.days_threshold = days_threshold
        self.price_threshold = price_threshold

    def apply_indicators(self, df):
        # Apply Bollinger Bands
        bb = ta.bbands(df['Close'], length=20)
        df['bb_upper'] = bb['BBU_20_2.0']
        df['bb_lower'] = bb['BBL_20_2.0']
        
        # Apply Keltner Channel
        kc = ta.kc(df['High'], df['Low'], df['Close'], length=20, scalar=2)
        df['kc_upper'] = kc['KCUe_20_2.0']
        df['kc_lower'] = kc['KCLe_20_2.0']
        
        # Apply Chaikin Oscillator
        df['chaikin'] = ta.adosc(df['High'], df['Low'], df['Close'], df['Volume'], fast=3, slow=10)
        
        # Apply 100-period Simple Moving Average
        df['sma_100'] = ta.sma(df['Close'], length=100)
        
        return df

    def generate_signals(self, df):
        # Generate buy signals (Enter Long)
        df['signal_long'] = np.where(
            (df['bb_upper'] < df['kc_upper']) &
            (df['bb_lower'] > df['kc_lower']) &
            (df['chaikin'] > 0) &
            (df['Close'] > df['sma_100']),
            1, 0
        )
        
        # Generate sell signals (Enter Short)
        df['signal_short'] = np.where(
            (df['bb_upper'] < df['kc_upper']) &
            (df['bb_lower'] > df['kc_lower']) &
            (df['chaikin'] < 0) &
            (df['Close'] < df['sma_100']),
            -1, 0
        )
        
        return df

    def execute(self, df):
        df = self.apply_indicators(df)
        df = self.generate_signals(df)
        buy_signals = df[df['signal_long'] == 1][['Close']]
        sell_signals = df[df['signal_short'] == -1][['Close']]
        return buy_signals, sell_signals
