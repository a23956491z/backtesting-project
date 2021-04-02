import pandas as pd
import numpy as np
import glob
from functools import partial

from tools import trade
from tools import readStock_file

from strategy import strategy

########  Basic Settings  ########
print_format = {'tradingRecord'     : True,
                'tradingNum'        : False,
                'fileName'          : True,
                'fileNameNewLine'   : True,
                'returnRate'        : True,
                }

file_pattern = "parse_data/data/splited/00*.csv"

choose_strategy = 'tripleMA_stopLoss'
########  Basic Settings  ########

########  Strategiy Configuration  ########
strategies = {
    'WMR' : partial(
        strategy.WMR,
        short_stop_loss=True),

    'Complete_KD' : partial(
        strategy.pure_KD,
        short_stop_loss=True,
        internal_indicator=True),

    'tripleMA_stopLoss' : partial(
        strategy.tripleMA_stopLoss,
        ma_window_short = 7,
        ma_window_mid = 15,
        ma_window_long = 21,
        tolerence_interval = 7),
}
########  Strategiy Configuration  ########

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
    ticker = readStock_file(data_file)

    dw = strategies[choose_strategy](ticker)

    bakctesting = derieved(dw, 0.001425, 0.003, 1,
                    print_trading=print_format['tradingRecord'],
                    print_tradingTimes=print_format['tradingNum'],
                    print_returnRate=print_format['returnRate'])
    bakctesting.run()
    result = bakctesting.result()
    if result:
        returnRates[data_file] = result

arr = np.fromiter(returnRates.values(), dtype=float)

print("\nFinal total return rate : {}%".format( round(arr.sum(), 4)));

returnRates = dict(sorted(returnRates.items(), key=lambda item: item[1], reverse=True))
print("Highest 3 return rate :")

counter = 0
for key, value in returnRates.items():
    print("\t\"{}\" return rate : {}%".format(key, value))
    counter = counter+1
    if counter == 3:
        break;
