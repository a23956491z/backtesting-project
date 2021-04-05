#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import glob
import talib

from tools import readStock_excel
from backtesting import Backtest
from backtesting import Strategy
from backtesting.lib import crossover

print_format = {'tradingRecord'     : False,
                'tradingNum'        : True,
                'fileName'          : True,
                'fileNameNewLine'   : True,
                'returnRate'        : True}

def SMA(values,n):
    """
    Return simple moving average of `values`, at
    each step taking into account `n` previous values.
    """
    return pd.Series(values).rolling(n).mean()
def KDJ_K(high, low, close):
    slowk, slowd = talib.STOCH(high,
                    low,
                    close,
                    fastk_period=9,
                    slowk_period=3,
                    slowk_matype=0,
                    slowd_period=3,
                    slowd_matype=0)
    return slowk
def KDJ_D(high, low, close):
    slowk, slowd = talib.STOCH(high,
                    low,
                    close,
                    fastk_period=9,
                    slowk_period=3,
                    slowk_matype=0,
                    slowd_period=3,
                    slowd_matype=0)
    return slowd
from datetime import datetime
class KDCross(Strategy):
# Define the two MA lags as *class variables*
# for later optimization

    holding = 0
    def init(self):
        # Precompute the two moving averages

        self.slowk = self.I(KDJ_K,self.data.High, self.data.Low, self.data.Close)
        self.slowd = self.I(KDJ_D,self.data.High, self.data.Low, self.data.Close)
    def next(self):

        if crossover(self.slowk, self.slowd) and self.slowd > 70 and self.holding==0:
            print("\t{} buy  : {}".format(datetime.strftime(self.data.index[-1],'%Y/%m/%d'), self.data.Close[-1]))
            self.position.close()
            self.buy()
            self.holding = 1

        elif crossover(self.slowd, self.slowk)  and self.slowd < 30 and self.holding:
            print("\t{} sell : {}".format(datetime.strftime(self.data.index[-1],'%Y/%m/%d'), self.data.Close[-1]))
            self.position.close()
            self.sell()
            self.holding = 0

returnRates = {}
for data_file in glob.glob("data/*.xlsx"):
#data_file = 'data/1325.xlsx'
    if print_format['fileName']:
        print(data_file, end='\n' if print_format['fileNameNewLine'] else '')
    ticker = readStock_excel(data_file)

    bakctesting = Backtest(ticker, KDCross,commission=.002,trade_on_close=True,)
    result = bakctesting.run()
    print("\tTrades : {}".format(result['# Trades']))
    print("\tReturn Rate : {}%".format(round(result['Return [%]'],4)))
