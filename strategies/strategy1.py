import pandas as pd
import numpy as np
import pandas_ta as ta
import config

class BollingerKeltnerChaikinSMAStrategy:
    """
    Bollinger-Keltner Chaikin SMA Strategy
    --------------------------------------
    This strategy combines Bollinger Bands, Keltner Channels, the Chaikin Oscillator, 
    and a Simple Moving Average (SMA) to generate long and short signals.
    
    The strategy goes long when the upper Bollinger Band is below the upper Keltner Band, 
    the lower Bollinger Band is above the lower Keltner Band, the Chaikin Oscillator is above 
    zero, and the 100-period SMA is rising. 

    It goes short when the opposite conditions are met.
    """

    def __init__(self):
        self.position_size = config.position_size
        self.stop_loss = config.stop_loss
        self.profit_target1 = config.profit_target1
        self.partial_sell1 = config.partial_sell1
        self.profit_target2 = config.profit_target2
        self.partial_sell2 = config.partial_sell2
        self.days_threshold = config.days_threshold
        self.price_threshold = config.price_threshold

    def apply_indicators(self, df):
        # Apply indicators
        bb = ta.bbands(df['Close'], length=20)
        df['bb_upper'] = bb['BBU_20_2.0']
        df['bb_lower'] = bb['BBL_20_2.0']
        
        kc = ta.kc(df['High'], df['Low'], df['Close'], length=20, scalar=2)
        df['kc_upper'] = kc['KCUe_20_2.0']
        df['kc_lower'] = kc['KCLe_20_2.0']
        
        df['chaikin'] = ta.adosc(df['High'], df['Low'], df['Close'], df['Volume'], fast=3, slow=10)
        
        df['sma_100'] = ta.sma(df['Close'], length=100)
        
        return df

    def generate_signals(self, df):
        # Generate long signals
        df['signal_long'] = np.where(
            (df['bb_upper'] < df['kc_upper']) &
            (df['bb_lower'] > df['kc_lower']) &
            (df['chaikin'] > 0) &
            (df['Close'] > df['sma_100']),
            1, 0
        )
        
        # Generate short signals
        df['signal_short'] = np.where(
            (df['bb_upper'] > df['kc_upper']) &
            (df['bb_lower'] < df['kc_lower']) &
            (df['chaikin'] < 0) &
            (df['Close'] < df['sma_100']),
            -1, 0
        )
        
        return df['signal_long'], df['signal_short']

    def execute(self, df):
        df = self.apply_indicators(df)
        long_signals, short_signals = self.generate_signals(df)
        return long_signals, short_signals
