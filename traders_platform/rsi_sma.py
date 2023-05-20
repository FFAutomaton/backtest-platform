from ta.trend import EMAIndicator, SMAIndicator
from ta.momentum import RSIIndicator
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
 

#warnings.filterwarnings('ignore')



exchange = ccxt.binanceus()

from_ts = exchange.parse8601('2023-02-01 00:00:00')

ohlcv = exchange.fetch_ohlcv('BTC/USDT', timeframe='4h', since = from_ts,  limit = 1000) #daily candles with 200 day.(200 candle)

ohlcv_list=[]

ohlcv_list.append(ohlcv)
while True:
    from_ts = ohlcv[-1][0]
    new_ohlcv = exchange.fetch_ohlcv('BTC/USDT', '4h', since=from_ts, limit=1000)
    ohlcv.extend(new_ohlcv)
    if len(new_ohlcv)!=1000:
        break

df= pd.DataFrame(ohlcv[:-1], columns= ['timestamp','Open', 'High', 'Low', 'Close', 'Volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

data = df

data = data.set_index('timestamp')

print("data checked.")


#####################################################33


def wma(df, length=20):
    result = ta.wma(df["High"], length)
    return result




class RsiEmaStrategy:
    def __init__(self):
        self.suanki_fiyat = None
        self.rsi_value = None
        self.ema_value_big = None
        self.ema_value_small = None
        self.rsi_emasi_value = None
        self.rsi_bounding_limit = 20
        self.ema_bounding_buyuk = 0.02
        self.ema_bounding_kucuk = 0.01
        self.momentum_egim_hesabi_window = 21
        self.trend_ratio = 0.003
        self.rsi_smasi_trend = 0
        self.prev_rsi_emasi = None
        self.tavan_yapti = 0
        self.dipten_dondu = False
        self.tavandan_dondu = False
        self.karar = 0

    def init_strategy(self, data):
        self.reset()
        # self.rsi_hesapla(series, rsi_w)
        # self.ema_hesapla(series, ema_w, ema_k)
        self.rsi_smasi_trend_hesapla(data, 31)
        self.tavandan_dondu_mu()
        self.tavan_yapti_mi()

    def reset(self):
        self.karar = 0
        self.rsi_smasi_trend = 0
        self.tavan_yapti = 0
        self.dipten_dondu = False
        self.tavandan_dondu = False
        # self.momentum_trend_rsi = 0

    def karar_hesapla(self, pozisyon):
        if pozisyon == 0 and self.tavan_yapti != 0:
            self.karar = 0
            return

        ema_alt_ust, ema_alt_ust_small = self.alt_ust_hesapla()

        if ema_alt_ust * ema_alt_ust_small < 0:
            if pozisyon != 0:
                self.karar = 3
                return
            self.karar = 0
            return

        if ema_alt_ust == -1:
            if (self.rsi_smasi_trend == -1 and self.rsi_value > self.rsi_bounding_limit):
                self.karar = -1
                return
            if ema_alt_ust_small == -1:
                self.karar = -1
                return
        if ema_alt_ust == 1:
            if (self.rsi_smasi_trend == 1 and self.rsi_value < 100 - self.rsi_bounding_limit):
                self.karar = 1
                return
            if ema_alt_ust_small == 1:
                self.karar = 1
                return
        """
        if self.tavandan_dondu:
            self.karar = -1
        elif self.dipten_dondu:
            self.karar = 1
        """
    def alt_ust_hesapla(self):
        ema_alt_ust = 0
        ema_alt_ust_small = 0
        if self.ema_value_big * (1 - self.ema_bounding_buyuk) > self.suanki_fiyat:
            ema_alt_ust = -1
        elif self.ema_value_big * (1 + self.ema_bounding_buyuk) < self.suanki_fiyat:
            ema_alt_ust = 1

        if self.ema_value_small * (1 - self.ema_bounding_kucuk) > self.suanki_fiyat:
            ema_alt_ust_small = -1
        elif self.ema_value_small * (1 + self.ema_bounding_kucuk) < self.suanki_fiyat:
            ema_alt_ust_small = 1
        return ema_alt_ust, ema_alt_ust_small

    def egim_hesapla(self):
        diff = []
        for i in range(0, self.momentum_egim_hesabi_window):
            diff.append(self.rsi_series[i] - self.rsi_series[i+1])
        if diff != 0 or len(diff) != 0:
            return round(float(sum(diff) / len(diff)), 2)
        return 0

    def rsi_smasi_trend_hesapla(self, data, window):
        self.rsi_emasi_series = ta.sma(pd.Series(data), length=window)
        self.rsi_emasi_value = self.rsi_emasi_series.iloc[-1]
        self.prev_rsi_emasi = self.rsi_emasi_series.iloc[-2]
        self.rsi_smasi_trend = 0
        if self.prev_rsi_emasi < self.rsi_emasi_value:
            self.diff = self.rsi_emasi_value - self.prev_rsi_emasi
            if self.diff == 0:
                return
            ratio = round(float(self.diff / self.rsi_emasi_value), 5)
            if ratio > self.trend_ratio:
                self.rsi_smasi_trend = 1
        else:
            self.diff = self.prev_rsi_emasi - self.rsi_emasi_value
            if self.diff == 0:
                return
            ratio = round(float(self.diff / self.prev_rsi_emasi), 5)
            if ratio > self.trend_ratio:
                self.rsi_smasi_trend = -1

    def tavandan_dondu_mu(self):
        prev_rsi = self.rsi_value_prev
        _rsi = self.rsi_value
        if prev_rsi < self.rsi_bounding_limit:
            if _rsi > self.rsi_bounding_limit:
                self.dipten_dondu = True
        elif prev_rsi > 100 - self.rsi_bounding_limit:
            if _rsi < 100 - self.rsi_bounding_limit:
                self.tavandan_dondu = True

    def tavan_yapti_mi(self):
        _rsi = self.rsi_value
        if _rsi > 100 - self.rsi_bounding_limit:
            self.tavan_yapti = 1
        if _rsi < self.rsi_bounding_limit:
            self.tavan_yapti = -1
