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
from utils import *
from services.data_service import CcxtDataService
from traders_ffautomaton.turtle import Turtle
import statistics


data = CcxtDataService.get_data('2023-03-01 00:00:00', 'ARB/USDT', '1h')
turtle = Turtle()


class TurtleStrategy(Strategy):
    atr_length = 20

    def init(self):
        self.atr_indicator = self.I(ATR, self.data.df, length=self.atr_length)

    def suanki_pozisyon_hesapla(self):
        if self.position.is_long:
            self.suanki_pozisyon = 1
        elif self.position.is_short:
            self.suanki_pozisyon = -1
        else:
            self.suanki_pozisyon = 0



    def next(self):
        turtle.son20_highest = max(self.data.Close[-20:])
        turtle.son20_lowest = min(self.data.Close[-20:])
        turtle.son10_highest = max(self.data.Close[-10:])
        turtle.son10_lowest = min(self.data.Close[-10:])
        turtle.suanki_fiyat = self.data.Close[-1]

        # turtle.init_strategy(self.data.Close)
        self.suanki_pozisyon_hesapla()
        turtle.karar_hesapla()
        turtle.cikis_kontrol(self.position)

        atr_mean = turtle.atr_mean_hesapla(self.atr_indicator, self.atr_length)
        size = turtle.miktar_hesapla(self.equity, atr_mean)
        # print(self.equity, size)

        if turtle.karar == 3:
            self.position.close()
            turtle.reset()
        elif not self.position.is_long and turtle.karar == 1:
            if self.position.is_long or self.position.is_short:
                self.position.close()
                turtle.reset()
            self.buy(size=size)
            turtle.giris_fiyat = turtle.suanki_fiyat
        elif not self.position.is_short and turtle.karar == -1:
            if self.position.is_long or self.position.is_short:
                self.position.close()
                turtle.reset()
            self.sell(size=size)
            turtle.giris_fiyat = turtle.suanki_fiyat

        if self.position.is_long:
            if turtle.suanki_fiyat >= turtle.giris_fiyat + (0.5 * atr_mean):
                if turtle.piramit <= 3:
                    turtle.piramit += 1
                    self.buy(size=size)
                    turtle.giris_fiyat = turtle.suanki_fiyat
        if self.position.is_short:
            if turtle.suanki_fiyat <= turtle.giris_fiyat - (0.5 * atr_mean):
                if turtle.piramit <= 3:
                    turtle.piramit += 1
                    self.sell(size=size)
                    turtle.giris_fiyat = turtle.suanki_fiyat


bt = Backtest(data, TurtleStrategy, cash=10_000_000, commission=.002, trade_on_close=True)

result = bt.run()
# bt.plot()

print(result)
print(
    '--------------------------------------------------------------------------------------------------------------------------------')
# print(result._trades)
# print(result._equity_curve)
print(
    '--------------------------------------------------------------------------------------------------------------------------------')

