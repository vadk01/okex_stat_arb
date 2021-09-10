import datetime
import ccxt
import calendar
import os
import json
import pandas as pd
import cointegration_calc
import schedule

import time
import okex.Account_api as Account
import okex.Funding_api as Funding
import okex.Market_api as Market
import okex.Public_api as Public
import okex.Trade_api as Trade
import okex.status_api as Status
import okex.subAccount_api as SubAccount

start_time = time.time()

api_key = "06345cf3-3721-4da8-813c-dfd1f5ba0ea6"
secret_key = "2D7057F7C65F8651D1D2F8C18A85251F"
passphrase = "vadim5365"
flag = '0'
path = 'data/'

marketAPI = Market.MarketAPI(api_key, secret_key, passphrase, False, flag)

exchange = ccxt.okex()
markets = exchange.load_markets()
columns = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'QuantityVol']

path = 'data/'
tickers = list()
for market in markets:
    if market[-9:] == "USDT-SWAP":
        tickers.append(market)



def add_new_rows(old_df, present_df):
    new_df = pd.concat([old_df, present_df])
    new_df.Datetime = new_df.Datetime.astype('int64')
    new_df.drop_duplicates(subset='Datetime', keep='first', inplace=True)
    return new_df

def download_data():

    print("Current time is:", datetime.datetime.now())
    if len(os.listdir(path=path)) != 0:
        for ticker in os.listdir(path=path):
            ticker = ticker[:-4]
            result = marketAPI.get_candlesticks(ticker, bar='4H')
            data = pd.DataFrame(result["data"], columns=columns)[::-1]
            old_data = pd.read_csv(path+ticker+'.csv', header=0)
            new_data = add_new_rows(old_data, data)
            new_data.to_csv(path+ticker+'.csv', index=False)
    else:
        for ticker in os.listdir(path=path):
            ticker = ticker[:-4]
            result = marketAPI.get_candlesticks(ticker, bar='4H')
            data = pd.DataFrame(result["data"], columns=columns)[::-1]
            #data.Datetime = pd.to_datetime(data.Datetime, unit='ms', origin='unix')
            data.to_csv(path+ticker+'.csv', index=False)
    cointegration_calc.create_quotes(path)

    print('Done in --- %s seconds ---' % (time.time() - start_time))
    print("Current time is:", datetime.datetime.now())