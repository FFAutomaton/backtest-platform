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


def wma(df, length=20):
    result = ta.wma(df["High"], length)
    return result

def wma2(df, length=20):
    result = ta.wma(df["Low"], length)
    return result

def wma3(df, length=30):
    result = ta.wma(df["High"], length)
    return result

def wma4(df, length=40):
    result = ta.wma(df["Low"], length)
    return result


#WMA Strategy
class WMAStrategy(Strategy):
    length1 = 144
    length2 = 233
    length3 = 34
    length4 = 21

    def init(self):
        
        self.wma11 = self.I(
            wma,
            self.data.df,
            length=self.length1,
            overlay=True
        )
        self.wma22 = self.I(
            wma2,
            self.data.df,
            length=self.length2,
            overlay=True
        )
        self.wma33 = self.I(
            wma3,
            self.data.df,
            length=self.length3,
            overlay=True
        )
        
        self.wma44 = self.I(
            wma4,
            self.data.df,
            length=self.length4,
            overlay=True
        )

    def next(self): 
        
        if not self.position.is_long and self.data.Close[-1]>self.wma11[-1] and self.data.Close[-1]>self.wma33:
            self.position.close()
            self.buy()
        elif not self.position.is_short and self.data.Close[-1]<self.wma22[-1] and self.data.Close[-1]<self.wma44:
            self.position.close()
            self.sell()

        

        """
        if self.data.Close[-1]>self.wma11[-1]:
            self.hlv1.append(int(1))
        else:
            if self.data.Close[-1]<self.wma22[-1]:
                self.hlv1.append(-1)
            else:
                self.hlv1.append(self.hlv1[-1] if self.hlv1[-1] else 0)
        
        if self.data.Close[-1]>self.wma33[-1]:
            self.hlv2.append(int(1))
        else:
            if self.data.Close[-1]<self.wma44[-1]:
                self.hlv2.append(-1)
            else:
                self.hlv2.append(self.hlv2[-1] if self.hlv2[-1] else 0)

        if self.hlv1[-1]==1 and self.hlv2[-1]==1:
            self.position.close()
            self.buy()
        elif self.hlv1[-1] == -1 and self.hlv2[-1] == -1:
            self.position.close()
            self.sell()
        """
        

bt = Backtest(data, WMAStrategy, cash=100_000, commission=.002, trade_on_close=True)

result= bt.run()
bt.plot()

print(result)
print('--------------------------------------------------------------------------------------------------------------------------------')
print(result._trades)
#print(result._equity_curve)
print('--------------------------------------------------------------------------------------------------------------------------------')
