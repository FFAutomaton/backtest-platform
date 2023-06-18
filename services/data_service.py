
import ccxt
import pandas as pd

class CcxtDataService:
    @staticmethod
    def get_data(start_date, pair, candle_window):
        exchange = ccxt.binance()

        from_ts = exchange.parse8601(start_date)

        ohlcv = exchange.fetch_ohlcv(pair, timeframe=candle_window, since = from_ts,  limit = 1000) #daily candles with 200 day.(200 candle)

        ohlcv_list=[]

        ohlcv_list.append(ohlcv)
        while True:
            from_ts = ohlcv[-1][0]
            new_ohlcv = exchange.fetch_ohlcv(pair, candle_window, since=from_ts, limit=1000)
            ohlcv.extend(new_ohlcv)
            if len(new_ohlcv)!=1000:
                break

        df= pd.DataFrame(ohlcv[:-1], columns= ['timestamp','Open', 'High', 'Low', 'Close', 'Volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        data = df

        data = data.set_index('timestamp')
        return data

