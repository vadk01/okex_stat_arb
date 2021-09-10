import pandas as pd
from math import ceil
import numpy as np
from sklearn.linear_model import LinearRegression
import scipy.stats as st
import okex.Account_api as Account
import okex.Trade_api as Trade

# api_key = "06345cf3-3721-4da8-813c-dfd1f5ba0ea6" # real trading
api_key = "a2aa66c7-7899-4d05-9e1f-060573e3c5a0"  # demo trading
# secret_key = "2D7057F7C65F8651D1D2F8C18A85251F" # real trading
secret_key = "20B83D7A49A7696F495D4A57285211E6"  # demo trading
passphrase = "vadim5365"
flag = '1'
path = 'data/'

coef_period = 500
period = 13
open_threshold = 2
close_threshold = 0.015
pair_balance = 80

min_amounts = pd.read_csv('min_amounts.csv', index_col=0)


def full_name(coin):
    return coin + '-USDT-SWAP.csv'


def coin_to_inst(coin):
    return coin + '-USDT-SWAP'


def open_pos(inst1, inst2, qty1, qty2, direction):
    if direction == 'short':
        result = tradeAPI.place_multiple_orders([
            {'instId': inst1, 'tdMode': 'isolated', 'side': 'sell', 'posSide': 'short', 'ordType': 'market',
             'sz': ceil(qty1 / min_amounts['MinAmount'].loc[inst1[:-10]])},
            {'instId': inst2, 'tdMode': 'isolated', 'side': 'buy', 'posSide': 'long', 'ordType': 'market',
             'sz': ceil(qty2 / min_amounts['MinAmount'].loc[inst2[:-10]])}
        ])
        print(result)

    if direction == 'long':
        result = tradeAPI.place_multiple_orders([
            {'instId': inst1, 'tdMode': 'isolated', 'side': 'buy', 'posSide': 'long', 'ordType': 'market',
             'sz': ceil(qty1 / min_amounts['MinAmount'].loc[inst1[:-10]])},
            {'instId': inst2, 'tdMode': 'isolated', 'side': 'sell', 'posSide': 'short', 'ordType': 'market',
             'sz': ceil(qty2 / min_amounts['MinAmount'].loc[inst2[:-10]])}
        ])
        print(result)


def close_pos(inst1, inst2, position):
    if position == 1:
        tradeAPI.close_positions(inst1, 'isolated', 'short', 'USDT')
        tradeAPI.close_positions(inst2, 'isolated', 'long', 'USDT')
    if position == -1:
        tradeAPI.close_positions(inst1, 'isolated', 'long', 'USDT')
        tradeAPI.close_positions(inst2, 'isolated', 'short', 'USDT')


accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)

balance = float(accountAPI.get_account('USDT')['data'][0]['details'][0]['cashBal'])
pairs = pd.read_csv('pairs.csv')
print('\n==================')
print('Balance is:', balance)
print('$ per pair:', balance / len(pairs))
print('================== \n')
# pair_balance = balance/len(pairs)

for row in range(len(pairs)):
    # print(pairs.Pair1.iloc[row], pairs.Pair2.iloc[row])
    position = pairs['Position'].iloc[row]
    coin1 = pairs["Pair1"].iloc[row]
    coin2 = pairs["Pair2"].iloc[row]
    data1_full = pd.read_csv(path + coin1 + '-USDT-SWAP.csv')[['Close']][:-1].reset_index()
    data2_full = pd.read_csv(path + coin2 + '-USDT-SWAP.csv')[['Close']][:-1].reset_index()
    data1 = np.array(data1_full.Close[-period:]).astype('float64').reshape(-1, 1)
    data2 = np.array(data2_full.Close[-period:]).astype('float64').reshape(-1, 1)
    data1_coef = np.array(data1_full.Close[-coef_period:]).astype('float64').reshape(-1, 1)
    data2_coef = np.array(data2_full.Close[-coef_period:]).astype('float64').reshape(-1, 1)
    LR = LinearRegression()
    LR.fit(data1_coef, data2_coef)
    spread = data2 - (data1 * LR.coef_[0][0]+ LR.intercept_[0])
    zscore = st.zscore(spread)[-1][0]
    value = 1000

    if LR.coef_[0][0] > 1:
        qty2 = value / (data1[-1] * LR.coef_[0][0] + LR.intercept_)
        qty1 = value / data1[-1]
    elif LR.coef_[0][0] <= 1:
        qty1 = value / data1[-1]
        qty2 = value / (data1[-1] * LR.coef_[0][0] + LR.intercept_)

    if position == 1:
        if zscore < -open_threshold:
            close_pos(coin_to_inst(coin1), coin_to_inst(coin2), position)
            open_pos(coin_to_inst(coin1), coin_to_inst(coin2), qty1[0], qty2[0], 'long')
            pairs.iat[row, 2] = -1
        elif -close_threshold < zscore < close_threshold:
            close_pos(coin_to_inst(coin1), coin_to_inst(coin2), position)
            pairs.iat[row, 2] = 0
    elif position == -1:
        if zscore > open_threshold:
            close_pos(coin_to_inst(coin1), coin_to_inst(coin2), position)
            open_pos(coin_to_inst(coin1), coin_to_inst(coin2), qty1[0], qty2[0], 'short')
            pairs.iat[row, 2] = 1
        elif -close_threshold < zscore < close_threshold:
            close_pos(coin_to_inst(coin1), coin_to_inst(coin2), position)
            pairs.iat[row, 2] = 0
    elif position == 0:
        if zscore < -open_threshold:
            close_pos(coin_to_inst(coin1), coin_to_inst(coin2), position)
            open_pos(coin_to_inst(coin1), coin_to_inst(coin2), qty1[0], qty2[0], 'long')
            pairs.iat[row, 2] = -1
        if zscore > open_threshold:
            close_pos(coin_to_inst(coin1), coin_to_inst(coin2), position)
            open_pos(coin_to_inst(coin1), coin_to_inst(coin2), qty1[0], qty2[0], 'short')
            pairs.iat[row, 2] = 1
    #print("Total position data:")
    #print("Pair: {}-{}, Prices: {}-{} \nLR Coef: {}, zscore: {}, Value: {}, \nqty1: {}, qty2: {}, PosInUsd: {}-{}".format(coin1, coin2, data1[-1], data2[-1], LR.coef_[0][0], zscore, value, qty1[0], qty2[0], qty1*data1[-1], qty2*data2[-1]))

try:
    coin_bal = pd.DataFrame(accountAPI.get_position_risk('SWAP')['data'][0]['posData']).drop(columns=['ccy', 'posId', 'instType', 'mgnMode'])
except KeyError:
    coin_bal = 'No positions opened.'
print('\n==================')
print(coin_bal)
print('==================')
