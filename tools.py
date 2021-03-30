import pandas as pd
import numpy as np
from datetime import datetime

def readStock_file(file, filetype='csv'):

    if filetype == 'excel':
        df = pd.read_excel(file, engine='openpyxl', parse_dates=True, header=None)
    else:
        df = pd.read_csv(file)

    colume_name = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    df.columns = colume_name
    df = df.set_index('Date')
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df = df.replace(r'^\s*-$', np.nan, regex=True)

    for col in df.columns:
        if(col=='Date'):
            continue;
        df[col] = np.array([float(x) for x in df[col]])

    return df

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
        self.returns = 0
        self.trading_nums = 0

    def buy(self):
        if((self.holding_limit == 0) or
            self.holding_tickers < self.holding_limit):

            if self.print_trading:
                print('\t{} buy  {}'.format(datetime.strftime(self.date,'%Y/%m/%d'),round(self.position['Close'] * (1 + self.comission),1)))

            if(self.principal == 0):
                self.principal = self.position['Close'] * (1 + self.comission)

            self.balance -= self.position['Close'] * (1 + self.comission)
            self.holding_tickers = self.holding_tickers + 1

        return None

    def sell(self):
        if(self.holding_tickers):
            if self.print_trading:
                print('\t{} sell {}'.format(datetime.strftime(self.date,'%Y/%m/%d'),round(self.position['Close'] * (1 - self.comission - self.tax),1)))

            self.balance += self.position['Close'] * (1 - self.comission - self.tax)

            self.returns += (self.balance/self.principal)
            #print("\t",round(self.balance,4), round(self.principal,2), round(self.balance/self.principal,4), round(self.returns,4))
            self.principal, self.balance = 0,0
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

            self.next()

        for _i in range(self.holding_tickers):
            self.sell()

    def result(self):


        return_rate = round(self.returns *100, 4)

        if self.print_tradingTimes:
            print("\ttrading times : ", self.trading_nums)

        if self.print_returnRate:
            print("\treturn rate : {r}%".format(r=return_rate))

        return return_rate


if __name__ == '__main__':


    df = readStock_excel('data/1325.xlsx')
    print(df)

    hey = trade(df, 0.001425, 0.003, 1)
    hey.run()

    print("return rate : {r}%".format(r=hey.result()))
