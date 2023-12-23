from backtesting import Backtest, Strategy
import pandas_ta as ta
import pandas as pd
import numpy as np
from datetime import time, timedelta, datetime
import ccxt
import numpy as np
import warnings
from backtesting.lib import crossover
import math
from ff_utils import *
from services.data_service import CcxtDataService
from traders_ffautomaton.turtle import Turtle
import statistics
import random


data = CcxtDataService.get_data('2022-06-13 00:00:00', 'ETH/USDT', '1d')


class RandomOrderStrategy(Strategy):
    def init(self):
        self.super_trend_indicator = self.I(superTrendLabel, self.data.df, length=14)

    def suanki_pozisyon_hesapla(self):
        if self.position.is_long:
            self.suanki_pozisyon = 1
        elif self.position.is_short:
            self.suanki_pozisyon = -1
        else:
            self.suanki_pozisyon = 0

    def next(self):
        karar = random.randint(-1, 1)
        self.suanki_pozisyon_hesapla()
        suanki_fiyat = self.data.Close[-1]
        # burda super trend degerlerine ulasiyoruz.
        super_trend = self.super_trend_indicator
        super_trend_karar = super_trend.tolist()[1][-1]
        super_trend_stop = super_trend.tolist()[0][-1]

        if self.suanki_pozisyon == 0:
            # if karar == 1 and super_trend_karar == 1:
            if karar == 1:
                self.buy() # size optional
            # elif karar == -1 and super_trend_karar == -1:
            elif karar == -1:
                self.sell()

        if self.suanki_pozisyon == 1:
            if suanki_fiyat < super_trend_stop:
                self.position.close()

        if self.suanki_pozisyon == -1:
            if suanki_fiyat > super_trend_stop:
                self.position.close()


bt = Backtest(data, RandomOrderStrategy, cash=10_000_000, commission=.002, trade_on_close=True)

result = bt.run()
bt.plot()

print(result)
# print(
#     '--------------------------------------------------------------------------------------------------------------------------------')
# print(result._trades)
# print(result._equity_curve)
# print(
#     '--------------------------------------------------------------------------------------------------------------------------------')

