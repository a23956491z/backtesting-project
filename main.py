import pandas as pd
import numpy as np
import glob

from tools import trade
from tools import readStock_excel

from strategy import *

print_format = {'tradingRecord'     : True,
                'tradingNum'        : True,
                'fileName'          : True,
                'fileNameNewLine'   : True,
                'returnRate'        : True}

class derieved(trade):

    def next(self):
        if(self.position['buy'] == 1):
            self.buy()
        if(self.position['sell'] == 1):
            self.sell()


returnRates = {}
for data_file in glob.glob("data/*.xlsx"):
    if print_format['fileName']:
        print(data_file, end='\n' if print_format['fileNameNewLine'] else '')
    ticker = readStock_excel(data_file)

    dw = WMR(ticker, short_stop_loss=True)

    bakctesting = derieved(dw, 0.001425, 0.003, 1,
                    print_trading=print_format['tradingRecord'],
                    print_tradingTimes=print_format['tradingNum'],
                    print_returnRate=print_format['returnRate'])
    bakctesting.run()
    result = bakctesting.result()
    if result:
        returnRates[data_file] = result

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
