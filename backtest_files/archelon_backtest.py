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
from services.data_service import CcxtDataService, BinanceService
from traders_ffautomaton.archelon_test import ArchelonTest
import statistics
from backtesting.lib import crossover

binance_service = BinanceService()

# data = CcxtDataService.get_data('2023-12-20 00:00:00', 'SOL/USDT', '1h')
data = binance_service.get_data('2023-12-10 00:00:00', 'SOLUSDT', '1h')
print(data)
bt = Backtest(data, ArchelonTest, cash=10_000_000, commission=.002, trade_on_close=True)

result = bt.run()
# bt.plot()
# print(result._trades)
# print(result._equity_curve)
