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


#RSI
def RSI(df, length=7):
    result = ta.rsi(df["Close"], length)
    return result

#EMA
def EMA(df, length=100):
    result = ta.ema(df["Close"], length)
    return result

#RSI-SMA
def rsi_sma(df, length=100):
    result = ta.sma(df["Close"], length)
    return result


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

def superTrendLabel(df, length=10, multiplier=3):
    return ta.supertrend(df["High"], df["Low"], df["Close"], length, multiplier)[
        f"SUPERT_{length}_{multiplier}.0"
    ]
