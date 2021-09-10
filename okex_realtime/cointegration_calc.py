import pandas as pd
import statsmodels.tsa.stattools as st
import numpy as np
import os
from tqdm import tqdm
import time

path = 'data/'

def create_quotes(path):
    datas = os.listdir(path)
    shape = [pd.read_csv(path + datas[0]).shape[0], len(datas)]
    quotes = pd.DataFrame(np.zeros(shape), columns=datas)
    for data in datas:
        df = pd.read_csv(path + data)
        quotes[data] = df.Close
    return quotes


def calc_coint(df, n_rows):
    shape = int(df.shape[1])
    coint = pd.DataFrame(np.zeros((shape, shape)), index=df.columns, columns=df.columns)
    for ticker1 in tqdm(df.columns):
        for ticker2 in df.columns:
            if ticker1 == ticker2:
                coint[ticker1].loc[ticker2] = 1
                coint[ticker2].loc[ticker1] = 1
            else:
                coint[ticker1].loc[ticker2] = st.coint(df[ticker1][-n_rows:], df[ticker2][-n_rows:])[1]
    return coint


def get_coint_pairs(coint_df, pval):
    pairs = []
    for ticker1 in coint_df.columns:
        for ticker2 in coint_df.index:
            if coint_df[ticker1].loc[ticker2] <= pval:
                pairs.append([ticker1[:-14], ticker2[:-14], coint_df[ticker1].loc[ticker2]])
    pairs = pd.DataFrame(pairs, columns = ['Pair1', 'Pair2', 'Cointegration'])
    return pairs


def add_coint(coint_db, coint_df):
    coint_db = coint_db.append([time.time, coint_df])
    return coint_db



#df = get_coint_pairs(calc_coint(create_quotes(path), len(create_quotes(path))), 0.001)
#df[['Pair1', 'Pair2']].to_csv('pairs.csv', index=False)
"""df = calc_coint(create_quotes(path), 1080)
for ticker1 in df.columns:
    for ticker2 in df.index:
        if df[ticker1].loc[ticker2] <= 0.0001:
            print(ticker1[:-14] , "and", ticker2[:-14], df[ticker1].loc[ticker2])"""

