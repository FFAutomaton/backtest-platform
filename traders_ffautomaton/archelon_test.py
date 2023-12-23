from abc import ABC

import pandas_ta as ta
from ff_utils.ff_queue import LimitedQueue
from backtesting import Backtest, Strategy
import pandas as pd


class ArchelonTest(Strategy):

    def __init__(self, broker, data, params):
        super().__init__(broker, data, params)
        self.current_candle = None
        self.window = 20  # const value
        self.series = LimitedQueue(maxsize=100)

        self.pyramid_count = 0
        self.last_10_lowest = 0.0
        self.last_10_highest = 0.0
        self.last_20_lowest = 0.0
        self.last_20_highest = 0.0

        self.atr_value = 0.0
        self.amount_from_config = 25.0

    def init(self):
        # initializing highes and lowss
        self.last_20_highest = self.data.High[0]
        self.last_10_highest = self.data.High[0]
        self.last_20_lowest = self.data.Low[0]
        self.last_10_lowest = self.data.Low[0]

    def next(self):
        my_index = self.data.index[-1]
        self.current_candle = self.data.df.iloc[my_index]
        self.series.put(self.current_candle)
        if self.series.full():
            self.update_turtle_state()
            if self.position.is_long:
                pass

            elif self.position.is_short:
                pass
            else:
                # no position condition check for position entry
                pass



    def update_turtle_state(self):
        temp_df = pd.DataFrame(self.series.queue)
        self.update_turtle_high_and_low(temp_df)
        self.ATR(temp_df)
        self.calculate_entry_amount()

    def ATR(self, data):
        indicator = ta.atr(high=data["High"], low=data["Low"], close=data["Close"], length=self.window,
                           mamode="EMA")
        values = indicator.tail(2).iloc[1]
        self.atr_value = values

    def calculate_stop_loss(self):
        if self.position.is_long:
            return self.last_10_lowest
        elif self.position.is_short:
            return self.last_10_highest

    def calculate_entry_amount(self):
        return float(self.amount_from_config * (1 / self.atr_value * 2))

    def update_turtle_high_and_low(self, data) -> None:
        self.last_20_highest = max(data.High[-20:])
        self.last_20_lowest = min(data.Low[-20:])
        self.last_10_highest = max(data.High[-10:])
        self.last_10_lowest = min(data.Low[-10:])
