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
from traders_ffautomaton.rsi_sma import RsiEmaStrategy
#warnings.filterwarnings('ignore')

data = CcxtDataService.get_data('2023-01-01 00:00:00','BTC/USDT','1h')
print(data)
sevki_rsi = RsiEmaStrategy()

class RSIStrategy(Strategy):
    rsi_length = 7
    ema_length_buyuk = 100
    ema_length_kucuk = 35
    strend_m = 1
    strend_l = 7

    def init(self):
        
        self.rsi_indicator = self.I(
            RSI,
            self.data.df,
            length=self.rsi_length,
        )
        self.ema_buyuk = self.I(
            EMA,
            self.data.df,
            length=self.ema_length_buyuk,
            overlay=True
        )
        self.ema_kucuk = self.I(
            EMA,
            self.data.df,
            length=self.ema_length_kucuk,
            overlay=True
        )
        self.supertrend = self.I(
            superTrendLabel,
            self.data.df,
            length=self.strend_l,
            multiplier = self.strend_m,
            overlay=True
        )

    def suanki_pozisyon_hesapla(self):
        if self.position.is_long:
            self.suanki_pozisyon = 1
            
        elif self.position.is_short:
            self.suanki_pozisyon = -1
        else:
            self.suanki_pozisyon = 0
        
    def next(self): 
        sevki_rsi.rsi_value = self.rsi_indicator.data.obj[-1]
        sevki_rsi.rsi_value_prev = self.rsi_indicator.data.obj[-2]
        sevki_rsi.ema_value_big = self.ema_buyuk.data.obj[-1]
        sevki_rsi.ema_value_small = self.ema_kucuk.data.obj[-1]
        sevki_rsi.suanki_fiyat = self.data.Close[-1]
        
        sevki_rsi.init_strategy(self.data.Close)
        self.suanki_pozisyon_hesapla()
        sevki_rsi.karar_hesapla(self.suanki_pozisyon)
        


        if self.position.is_long and sevki_rsi.karar == -1 :
            self.position.close()
        elif self.position.is_short and sevki_rsi.karar == 1 :
            self.position.close()

        elif self.position.is_long and self.data.Close[-1] < self.supertrend[-1] :
            self.position.close()
        elif self.position.is_short and self.data.Close[-1] > self.supertrend[-1] :
            self.position.close()    

        elif not self.position.is_long and sevki_rsi.karar == 1 and self.data.Close[-1] > self.supertrend[-1] :
            self.buy()
        elif not self.position.is_short and sevki_rsi.karar == -1 and self.data.Close[-1] < self.supertrend[-1] :

            self.sell()
        

bt = Backtest(data, RSIStrategy, cash=100_000, commission=.002, trade_on_close=True)

result= bt.run()
bt.plot()

print(result)
print('--------------------------------------------------------------------------------------------------------------------------------')
print(result._trades)
#print(result._equity_curve)
print('--------------------------------------------------------------------------------------------------------------------------------')

