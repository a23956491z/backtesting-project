
# %%
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
from mpl_finance import candlestick2_ohlc

# TEJ 6530 2020/08/01-2020/12/11
ticker = pd.read_csv('data/tejdb_20201214164506.csv', index_col = 'Date', parse_dates = True)

kd_n = 9

rsv_list = []


for i in range(0, ticker.shape[0]):

    if i+kd_n >= ticker.shape[0]:
        # lowest = min(ticker.iloc[i:]['Close'])
        # highest = max(ticker.iloc[i:]['Close'])
        # if highest - lowest == 0:
        #     rsv =
        # else :
        #     rsv = (ticker.iloc[i]['Close'] - lowest) / (highest - lowest) * 100
        rsv = np.nan
    else:
        #print(i,i+kd_n,ticker.iloc[i:i+kd_n]['Close'])
        lowest = min(ticker.iloc[i:i+kd_n]['Close'])
        highest = max(ticker.iloc[i:i+kd_n]['Close'])
        rsv = (ticker.iloc[i]['Close'] - lowest) / (highest - lowest) * 100


    rsv_list.append(rsv)

ticker['RSV'] = rsv_list
print(ticker)


def calculate_k(lst, ticker, i):

    if i == ticker.shape[0]-1:
        k = 50
    elif np.isnan(ticker.iloc[i]['RSV']):
        calculate_k(lst, ticker, i+1)
        k = 50
    else:
        k = calculate_k(lst, ticker, i+1)*2/3 + ticker.iloc[i]['RSV']*1/3
    lst.insert(0, k)
    return k

def calculate_d(lst, k_list, ticker, i):

    if i == ticker.shape[0]-1:
        k = 50
    elif np.isnan(ticker.iloc[i]['RSV']):
        calculate_d(lst,k_list, ticker, i+1)
        k = 50
    else:
        k = calculate_d(lst, k_list,ticker, i+1)*2/3 + k_list[i]*1/3
    lst.insert(0, k)
    return k

k_list = []
d_list = []
calculate_k(k_list, ticker, 0)
calculate_d(d_list, k_list, ticker, 0)
ticker['k'] = k_list
ticker['d'] = d_list

ticker


# %%
ticker.sort_index(inplace=True)

fig = mpf.figure(figsize = (10,8))


apd = mpf.make_addplot( ticker[['k', 'd']])
index  = mpf.make_addplot(ticker[['k', 'd']],ylabel='KD', panel=1)

mpf.plot(ticker,ax=ax1, type = 'candle', style = 'yahoo', addplot = [index,apd], volume=ax3)


ax2.legend( ['k', 'd'])
