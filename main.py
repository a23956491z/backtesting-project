
# %%
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import talib
import mplfinance as mpf

# %%

def preprocess(file):

    df = pd.read_excel(file, engine='openpyxl', parse_dates=True, header=None)
    colume_name = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    df.columns = colume_name
    df = df.set_index('Date')

    for col in df.columns:
        if(col=='Date'):
            continue;
        df[col] = np.array([float(x) for x in df[col]])

    return df

ticker = preprocess('data/1325.xlsx')
print(ticker)

# %%
class trade:

    __comission = 0
    def __init__(self, ticker ,comission=0, tax=0, holding_limit=0,
                    print_trading=False, print_returnRate=False, print_tradingTimes=False):


        self.comission = comission
        self.tax = tax
        self.ticker = ticker
        self.holding_limit = holding_limit

        self.print_trading = print_trading
        self.print_returnRate = print_returnRate
        self.print_tradingTimes = print_tradingTimes

        self.principal = 0
        self.balance = 0
        self.holding_tickers = 0

        self.trading_nums = 0

    def buy(self):
        if((self.holding_limit == 0) or
            self.holding_tickers < self.holding_limit):

            if self.print_trading:
                print('\t{} buy  {}'.format(self.date,self.position['Close']))

            if(self.principal == 0):
                self.principal = self.position['Close']

            self.balance -= self.position['Close'] * (1+self.comission)
            self.holding_tickers = self.holding_tickers + 1

        return None

    def sell(self):
        if(self.holding_tickers):
            if self.print_trading:
                print('\t{} sell {}'.format(self.date,self.position['Close']))

            self.balance += self.position['Close'] * (1 - self.comission - self.tax)
            self.holding_tickers = self.holding_tickers - 1;

            self.trading_nums = self.trading_nums+1
        return None
    def next(self):

        self.buy()
        self.buy()
        self.sell()
        return None

    def run(self):
        for index, row in self.ticker.iterrows():
            self.position = row
            self.date = index

            close_price = self.position['Close']
            self.next()

        self.sell()

    def result(self):
        if(self.principal):
            return_rate = self.balance / self.principal
            return_rate = round(return_rate*100, 4)

            if self.print_tradingTimes:
                print("\ttrading times : ", self.trading_nums)

            if self.print_returnRate:
                print("\treturn rate : {r}%".format(r=return_rate))

            return return_rate
        return None


df = preprocess('data/1325.xlsx')
hey = trade(df, 0.001425, 0.003, 1)
hey.run()

print("return rate : {r}%".format(r=hey.result()))

# %%
import glob


class derieved(trade):

    def next(self):
        if(self.position['buy'] == 1):
            self.buy()
        if(self.position['sell'] == 1):
            self.sell()


returnRates = {};
for data_file in glob.glob("data/*.xlsx"):

    print(data_file)
    ticker = preprocess(data_file)

    short_window = 9
    long_window = 9
    dw = ticker
    dw['slowk'], dw['slowd'] = talib.STOCH(
    			ticker['High'].values,
    			ticker['Low'].values,
    			ticker['Close'].values,
                            fastk_period=short_window,
                            slowk_period=long_window,
                            slowk_matype=0.0,
                            slowd_period=long_window,
                            slowd_matype=0.0)


    signals = pd.DataFrame(index=dw.index)
    signals['signal'] = 0.0
    signals['slowk'] = dw['slowk']
    signals['slowd'] = dw['slowd']
    signals['signal'][short_window:]  = np.where((signals['slowk'][short_window:]
                                                > signals['slowd'][short_window:]), 1.0, 0.0)
    signals['positon'] = signals['signal'].diff()
    signals['buy'] = np.where((signals['slowk'] > 70) & (signals['positon'] == 1 ), 1.0, 0.0)
    signals['sell'] = np.where((signals['slowk'] < 30) & (signals['positon'] == -1 ), 1.0, 0.0)

    dw['buy'] = signals['buy']
    dw['sell'] = signals['sell']
    hey = derieved(dw, 0.001425, 0.003, 1, print_tradingTimes=True, print_returnRate=True)
    hey.run()
    returnRates[data_file] = hey.result()

arr = np.fromiter(returnRates.values(), dtype=float)

print("\nFinal total return rate : {}%".format( arr.sum()));

returnRates = dict(sorted(returnRates.items(), key=lambda item: item[1], reverse=True))
print("Highest 3 return rate :")

counter = 0
for key, value in returnRates.items():
    print("\t\"{}\" return rate : {}%".format(key, value))
    counter = counter+1
    if counter == 3:
        break;
