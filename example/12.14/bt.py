#%%
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd

import os
import numpy as np
import matplotlib.pyplot as plt


#%%
def SMA(values, n):
    """
    Return simple moving average of `values`, at
    each step taking into account `n` previous values.
    """
    return pd.Series(values).rolling(n).mean()

class SmaCross(Strategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 24
    n2 = 32

    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)

    def next(self):
        # If sma1 crosses above sma2, close any existing
        # short trades, and buy the asset
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()

        # Else, if sma1 crosses below sma2, close any existing
        # long trades, and sell the asset
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()

#%%
import re

def custom_report(stats, prefix):
    # print(prefix,'資產總額 : \t', round(stats['Equity Final [$]'],3))
    # print(prefix,'投報率 : \t', round(stats['Return [%]'],3) ,'%')
    # print(prefix,'交易次數 : \t',stats['# Trades'])
    # print(prefix,'勝率 : \t', round(stats['Win Rate [%]'], 3), '%')
    # print(prefix,'資產最高紀錄 : \t', round(stats['Equity Peak [$]'], 3))

    lst = []
    lst.append(round(stats['Equity Final [$]']))
    lst.append(round(stats['Return [%]'],3))
    lst.append(stats['# Trades'])
    lst.append(round(stats['Win Rate [%]'], 3))
    lst.append(round(stats['Equity Peak [$]'], 3))
    lst.append(round(stats['SQN'], 3))
    lst.append('n1 : '+str(stats['_strategy'].n1)+' n2 : '+str(stats['_strategy'].n2))

    return lst


#%%
tickers = { '2317鴻海':'data/tejdb_20201216193116.csv',
            '1101台泥':'data/tejdb_20201216200707.csv',
            '3045台灣大':'data/tejdb_20201216201053.csv',
            '4904遠傳':'data/tejdb_20201216204245.csv',
            '2454聯發科':'data/tejdb_20201216210131.csv',
            '2498宏達電':'data/tejdb_20201216204541.csv'}

report = pd.DataFrame(columns=['資產總額', '投報率', '交易次數', '勝率','資產最高紀錄','SQN', 'Strategy'])
time = 0
stra = 0
for key, value in tickers.items():

    ticker = pd.read_csv(value, index_col = 'Date', parse_dates = True)
    ticker.sort_index(inplace = True)

    bt = Backtest(ticker, SmaCross, cash=10000, commission=.004)
    stats = bt.optimize(n1=range(5, 30, 5),
                        n2=range(10, 70, 5),
                        maximize='Equity Final [$]',
                        constraint=lambda param: param.n1 < param.n2)
    time = [stats['Start'], stats['End']]
    report.loc[key] = custom_report(stats,'\t')

print('From : ', time[0])
print('To : ', time[1])

print()
report


# #%%
# ticker = pd.read_csv('data/tejdb_20201216193116.csv', index_col = 'Date', parse_dates = True)
# ticker.sort_index(inplace = True)
# ticker
#
# #%%
# bt = Backtest(ticker, SmaCross, cash=10000, commission=.004)
# stats = bt.run()
# stats = bt.optimize(n1=range(5, 30, 5),
#                     n2=range(10, 70, 5),
#                     maximize='Equity Final [$]',
#                     constraint=lambda param: param.n1 < param.n2)
# print(stats)
#
# #%%
# print(stats['_strategy'])
