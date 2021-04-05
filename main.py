#!/usr/bin/python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import glob
from functools import partial

from tools import trade
from tools import readStock_file

from strategy import strategy

########  Basic Settings  ########
print_format = {'tradingRecord'     : True, # 交易記錄
                'tradingNum'        : False,# 交易次數
                'fileName'          : True, # 逐一顯示檔案名稱
                'fileNameNewLine'   : True, # 每一個檔案跑完是否加換行
                'returnRate'        : True, # 投資報酬率
                }

# 用正則表示式表示有哪些檔案
file_pattern = "parse_data/data/splited/00*.csv"

# 選取下列策略中的哪一個
choose_strategy = 'tripleMA_stopLoss'
########  Basic Settings  ########

########  Strategiy Configuration  ########

# 用functools.partial()把function的參數儲存起來
# 之後呼叫就不需要再傳入重複的參數
strategies = {
    'WMR' : partial(
        strategy.WMR,
        short_stop_loss=True),      # 移動停損

    'Complete_KD' : partial(
        strategy.pure_KD,
        short_stop_loss=True,       # 移動停損
        internal_indicator=True),   # 使用手刻的KD指標

    'tripleMA_stopLoss' : partial(
        strategy.tripleMA_stopLoss,
        ma_window_short = 7,        # 第一條均線的區間
        ma_window_mid = 15,         # 第二條均線的區間
        ma_window_long = 21,        # 第三條均線的區間
        tolerence_interval = 7),    # 金三角的容許範圍
}
########  Strategiy Configuration  ########

# 在新的 class中表示出什麼時候買
# 例如 當self.position的買入信號是1的時候買
class derieved(trade):

    def next(self):
        if(self.position['buy'] == 1):
            self.buy()
        if(self.position['sell'] == 1):
            self.sell()


returnRates = {}
for data_file in glob.glob(file_pattern):

    if print_format['fileName']:
        print(data_file, end='\n' if print_format['fileNameNewLine'] else '')

    # 自己寫的 tools.readStock_file
    ticker = readStock_file(data_file)

    dw = strategies[choose_strategy](ticker)

    # 手續費是0.1425%
    # 股票交易稅是0.3%
    # 持有上限是1
    bakctesting = derieved(dw, 0.001425, 0.003, 1,
                    print_trading=print_format['tradingRecord'],
                    print_tradingTimes=print_format['tradingNum'],
                    print_returnRate=print_format['returnRate'])


    bakctesting.run()

    # result()會傳回投資報酬率
    # 同時也會 print出交易記錄等資訊
    result = bakctesting.result()

    # 如果投報率非 None
    # 便存入 returnRates 這個dictionary
    if result:
        returnRates[data_file] = result

# 把 returnRates 內所有的投報率轉換成 numpy 陣列
returnRates_arr = np.fromiter(returnRates.values(), dtype=float)
# 用 numpy 加總
final_return_rate = round(returnRates_arr.sum(), 4)

print("\nFinal total return rate : {}%".format(final_return_rate))

# 依照 投報率 進行排序，由高到低
returnRates = dict(sorted(returnRates.items(), key=lambda item: item[1], reverse=True))
print("Highest 3 return rate :")

# 列出 top3 的投報率
counter = 0
for key, value in returnRates.items():
    print("\t\"{}\" return rate : {}%".format(key, value))
    counter = counter+1
    if counter == 3:
        break;
