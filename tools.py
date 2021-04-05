import pandas as pd
import numpy as np
from datetime import datetime

def readStock_file(file, filetype='csv'):


    if filetype == 'excel':
        df = pd.read_excel(file, engine='openpyxl', parse_dates=True, header=None)
    else:
        df = pd.read_csv(file)

    # 取代原本的 column 名稱
    # 檔案的日期與開高低收需要照這個順序
    colume_name = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    df.columns = colume_name

    # 用日期這一行當做 df 的索引
    df = df.set_index('Date')

    # 把日期轉成 datetime的格式(從string)
    df.index = pd.to_datetime(df.index)

    # 照日期排序並把空資料轉成numpy的nan
    df = df.sort_index()
    df = df.replace(r'^\s*-$', np.nan, regex=True)


    for col in df.columns:
        if(col=='Date'):
            continue;
        df[col] = np.array([float(x) for x in df[col]])

    return df


class trade:

    __comission = 0
    """
    建構式參數：
        ticker 是放了股價資料的 pandas dataframe
        comission 是手續費
        tax 是交易稅
        holding_limit 是持有股票上限
        print_trading 是否在result()時 印出交易資料
        print_returnRate 是否在result()時 印出投資報酬率
        print_tradingTimes 是否在result()時 印出交易次數

    成員變數：
        principal 股票購入金額
        balance 餘額
        holding_tickers 持有股票數量
        returns 投資報酬率
        trading_nums 交易次數
    """
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

    """
    模擬買入股票
    這裡會印出買入的日期與價格

    操作流程：
        購入金額設為 含手續費的當日收盤價
        餘額減去 含手續費的當日收盤價
        股票持有數量加一
    """
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

    """
    模擬賣出股票
    這裡會印出賣出的日期與價格

    操作流程：
        購入金額設為 含手續費的當日收盤價
        餘額加回 含手續費與交易稅的當日收盤價
        股票持有數量減一
        交易次數加一(買入+賣出算一次)

        投報率算法：餘額 / 購入金額
        累計投報率：把所有投報率"加起來"
    """
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

    """
    run()的時候，會在每一個日期逐一執行next
    實際在使用的時候需要複寫這個函式(用繼承的方式)
    否則會使用預設的next()

    預設：
        不論條件，每天買兩次賣一次
    """
    def next(self):

        self.buy()
        self.buy()
        self.sell()
        return None

    """
    在每一個日期逐一執行 next()
    而next()內會判斷是否需要在當天進行買入或賣出
    """
    def run(self):
        for index, row in self.ticker.iterrows():
            self.position = row
            self.date = index

            self.next()

        for _i in range(self.holding_tickers):
            self.sell()

    """
    返回投資報酬率
    並依照條件印出相關交易資料
    """
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
