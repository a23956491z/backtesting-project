
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
    def __init__(self, ticker ,comission=0, tax=0, holding_limit=0):


        self.comission = comission
        self.tax = tax
        self.ticker = ticker
        self.holding_limit = holding_limit

        self.principal = 0
        self.balance = 0
        self.holding_tickers = 0

        self.close_price = 0
        self.buy_and_sell = 0

    def buy(self):
        if((self.holding_limit == 0) or
            self.holding_tickers < self.holding_limit):

            if(self.principal == 0):
                self.principal = self.close_price

            self.balance -= self.close_price * (1+self.comission)
            self.holding_tickers = self.holding_tickers + 1

        return None

    def sell(self):
        if(self.holding_tickers):
            self.balance += self.close_price * (1 - self.comission - self.tax)
            self.holding_tickers = self.holding_tickers - 1;

            self.buy_and_sell = self.buy_and_sell+1
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
            self.close_price = row['Close']
            self.next()

        self.sell()

    def result(self):
        if(self.principal):
            return_rate = self.balance / self.principal
            return_rate = round(return_rate*100, 4)
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
            print('\t{} buy {}'.format(self.date,self.position['Close']))
            self.buy()
        if(self.position['sell'] == 1):
            print('\t{} sell {}'.format(self.date,self.position['Close']))
            self.sell()

    def result(self):
        if(self.principal):
            return_rate = self.balance / self.principal
            return_rate = round(return_rate*100, 4)
            print("\ttrading times : ", self.buy_and_sell)
            print("\treturn rate : {r}%".format(r=return_rate))
        else:
            print("\tNo trading records!!")


for data_file in glob.glob("data/*.xlsx"):

    print(data_file)
    ticker = preprocess(data_file)

    short_window = 3
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
    signals['buy'] = np.where((signals['slowk'] > 60) & (signals['positon'] == 1 ), 1.0, 0.0)
    signals['sell'] = np.where((signals['slowk'] < 30) & (signals['positon'] == -1 ), 1.0, 0.0)

    dw['buy'] = signals['buy']
    dw['sell'] = signals['sell']
    hey = derieved(dw, 0.001425, 0.003, 1)
    hey.run()
    hey.result()
