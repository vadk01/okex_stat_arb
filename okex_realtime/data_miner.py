import ccxt
import pandas as pd
import calendar
import datetime
import os
from tqdm import tqdm
import okex.Market_api as Market
api_key = "06345cf3-3721-4da8-813c-dfd1f5ba0ea6"
secret_key = "2D7057F7C65F8651D1D2F8C18A85251F"
passphrase = "vadim5365"
flag = '0'

marketAPI = Market.MarketAPI(api_key, secret_key, passphrase, False, flag)

path = 'data/'
datas = os.listdir(path)

exchange = ccxt.okex()
markets = exchange.load_markets()
columns = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'QuantityVol']

now = datetime.datetime.utcnow()
unixtime = calendar.timegm(now.utctimetuple())
since = (unixtime - 60 * 60) * 1000 - 14400000 * 1400  # UTC timestamp in milliseconds

def add_new_rows(old_df, present_df):
    new_df = pd.concat([old_df, present_df])
    new_df.Datetime = new_df.Datetime.astype('int64')
    new_df.drop_duplicates(subset='Datetime', keep='last', inplace=True)
    return new_df

for period in tqdm(range(100, 1400, 100)):
    for ticker in datas:
        ticker = ticker[:-4]
        result = marketAPI.get_candlesticks(ticker, bar='4H', after=1629273600000 - 14400000 * period, limit=100)
        data = pd.DataFrame(result["data"], columns=columns)[::-1]
        old_data = pd.read_csv(path + ticker + '.csv', header=0)
        new_data = add_new_rows(data, old_data)
        new_data.to_csv(path + ticker + '.csv', index=False)

