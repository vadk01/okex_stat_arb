import ccxt
import pandas as pd
from tqdm import tqdm

a = list()
exchange = ccxt.okex()
markets = exchange.load_markets()
for market in tqdm(exchange.fetch_markets()):
    if market['id'][-9:] == 'USDT-SWAP':
        a.append([market['symbol'][:-10], market['info']['contract_val'],
                  round(exchange.fetch_ohlcv(market['symbol'])[-1][-2] * float(market['info']['contract_val']), 2)])

df = pd.DataFrame(a, columns=['Ticker', 'MinAmount', 'MinValue'])
df.to_csv('min_amounts.csv', index=False)
