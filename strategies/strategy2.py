import pandas as pd
import numpy as np
import pandas_ta as ta
from backtesting import Strategy

class LongOnlyBollingerKeltnerChaikinSMAStrategy(Strategy):
    """
    Long Only Bollinger-Keltner Chaikin SMA Strategy
    --------------------------------------
    This strategy combines Bollinger Bands, Keltner Channels, the Chaikin Oscillator, 
    and a Simple Moving Average (SMA) to generate long signals.
    
    The strategy goes long when the upper Bollinger Band is below the upper Keltner Band, 
    the lower Bollinger Band is above the lower Keltner Band, the Chaikin Oscillator crosses above 
    zero, and the 100-period SMA is rising.
    """

    def init(self):
        # Debugging: Print data before applying indicators
        print("Initializing strategy...")
        print(self.data.df.head())

        # Apply Bollinger Bands
        close_prices = pd.Series(self.data.Close)
        print("Close prices:")
        print(close_prices.head())

        bb = ta.bbands(close_prices, length=20)
        if bb is not None:
            print("Bollinger Bands calculated:")
            print(bb.head(25))  # Print first 25 values to see the NaNs and valid data
            self.bb_upper = self.I(lambda x: bb['BBU_20_2.0'].values, self.data.Close)
            self.bb_lower = self.I(lambda x: bb['BBL_20_2.0'].values, self.data.Close)
        else:
            raise ValueError("Bollinger Bands calculation returned None")

        # Apply Keltner Channels
        high_prices = pd.Series(self.data.High)
        low_prices = pd.Series(self.data.Low)
        kc = ta.kc(high_prices, low_prices, close_prices, length=20, scalar=2)
        if kc is not None:
            print("Keltner Channels calculated:")
            print(kc.head(25))  # Print first 25 values to see the NaNs and valid data
            self.kc_upper = self.I(lambda x: kc['KCUe_20_2.0'].values, self.data.Close)
            self.kc_lower = self.I(lambda x: kc['KCLe_20_2.0'].values, self.data.Close)
        else:
            raise ValueError("Keltner Channels calculation returned None")

        # Apply Chaikin Oscillator
        volume = pd.Series(self.data.Volume)
        self.chaikin = self.I(ta.adosc, high_prices, low_prices, close_prices, volume, fast=3, slow=10)

        # Apply 100-period SMA
        self.sma_100 = self.I(ta.sma, close_prices, length=100)
        
        # Initialize stop-loss and tracking variables
        self.stop_loss = None
        self.entry_price = None
        self.partial_sell_1 = None
        self.partial_sell_2 = None
        self.entry_time = None

    def next(self):
        # Calculate stop-loss price if not already set
        if self.position:
            if self.stop_loss is None:
                self.stop_loss = self.data.Close[-1] * 0.95  # 5% stop-loss
                self.entry_price = self.data.Close[-1]
                self.entry_time = self.data.index[-1]

            # Partial Sell Conditions
            current_price = self.data.Close[-1]
            if self.partial_sell_1 is None and current_price >= 2 * self.entry_price:
                self.sell(size=self.position.size * 0.5)
                self.stop_loss = self.entry_price * 1.2
                self.partial_sell_1 = current_price
            elif self.partial_sell_1 is not None and self.partial_sell_2 is None and current_price >= 2.5 * self.entry_price:
                self.sell(size=self.position.size * 0.5)
                self.stop_loss = self.partial_sell_1 * 1.2
                self.partial_sell_2 = current_price
            elif self.partial_sell_2 is not None and current_price >= 3 * self.entry_price:
                self.position.close()

            # Exit if price increase is not > 5% after 10 days
            if self.entry_time is not None and (self.data.index[-1] - self.entry_time).days >= 10:
                if (current_price / self.entry_price) <= 1.05:
                    self.position.close()
                    self.stop_loss = None
                    self.entry_price = None
                    self.partial_sell_1 = None
                    self.partial_sell_2 = None
                    self.entry_time = None

            elif self.position.is_long:
                if current_price < self.stop_loss:
                    self.position.close()
                    self.stop_loss = None
                    self.entry_price = None
                    self.partial_sell_1 = None
                    self.partial_sell_2 = None
                    self.entry_time = None

        # Check if the 100 SMA is rising
        sma_rising = self.sma_100[-1] > self.sma_100[-2]

        # Buy signal
        if (self.bb_upper[-1] < self.kc_upper[-1] and
            self.bb_lower[-1] > self.kc_lower[-1] and
            self.chaikin[-2] < 0 and self.chaikin[-1] > 0 and  # Chaikin Oscillator crosses above zero
            sma_rising):
            self.buy()
            self.stop_loss = self.data.Close[-1] * 0.95  # Set stop-loss for long position
            self.entry_price = self.data.Close[-1]
            self.entry_time = self.data.index[-1]
