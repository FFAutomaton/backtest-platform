from config import *
import ccxt
import pandas as pd
from ffautmaton_packages.binance_service import FFAutomatonBinanceService


class CcxtDataService:
    @staticmethod
    def get_data(start_date, pair, candle_window):
        exchange = ccxt.binance()

        from_ts = exchange.parse8601(start_date)

        ohlcv = exchange.fetch_ohlcv(pair, timeframe=candle_window, since=from_ts,
                                     limit=1000)  # daily candles with 200 day.(200 candle)

        ohlcv_list = []

        ohlcv_list.append(ohlcv)
        while True:
            from_ts = ohlcv[-1][0]
            new_ohlcv = exchange.fetch_ohlcv(pair, candle_window, since=from_ts, limit=1000)
            ohlcv.extend(new_ohlcv[1:]) #removed replicated dates.
            if len(new_ohlcv) != 1000:
                break

        df = pd.DataFrame(ohlcv[:-1], columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        data = df

        data = data.set_index('timestamp')
        return data


class BinanceService:
    def __init__(self):
        self.base_url = "https://fapi.binance.com"
        self.secrets = {"API_KEY": API_KEY, "API_SECRET": API_SECRET}
        self.ffautomaton_binance_service = FFAutomatonBinanceService(self.secrets)
        self.api_key = API_KEY
        self.secret_key = API_SECRET
        self.client = self.ffautomaton_binance_service.get_client()

    def get_data(self, start_date, pair, candle_window):
        candles = pd.DataFrame(self.client.get_historical_klines(pair, candle_window, start_date))
        candles.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_time', 'Quote_asset_volume',
                           'Number_of_trades', 'Taker_buy_base_asset_volume', 'Taker_buy_quote_asset_volume',
                           'Ignore']
        candles['High'] = pd.to_numeric(candles['High'])
        candles['Low'] = pd.to_numeric(candles['Low'])
        candles['Close'] = pd.to_numeric(candles['Close'])
        candles['Open'] = pd.to_numeric(candles['Open'])
        candles['Readable_time'] = pd.to_datetime(candles['Time'], unit='ms')
        candles = candles.drop(columns=['Close_time', 'Quote_asset_volume',
                                        'Number_of_trades', 'Taker_buy_base_asset_volume',
                                        'Taker_buy_quote_asset_volume',
                                        'Ignore'])
        return candles
