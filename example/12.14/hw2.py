import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
from mpl_finance import candlestick2_ohlc

# TEJ 6530 2020/08/01-2020/12/11
ticker = pd.read_csv('data/tejdb_20201216210131.csv', index_col = 'Date', parse_dates = True)
ticker['Volume'] = [int(i.replace(',', '')) for i in ticker['Volume']]
ticker.sort_index(inplace = True)
kd_n = 30
RSV_t = 10
K_t = 10

tmp = pd.DataFrame(index=ticker.index)
tmp['max_close'] = ticker['Close'].rolling(kd_n).max()
tmp['min_close'] = ticker['Close'].rolling(kd_n).min()
tmp['RSV'] = (ticker['Close'] - tmp['min_close'])/(tmp['max_close']-tmp['min_close'])*100

ticker['k'] = tmp['RSV'].rolling(RSV_t).mean()
ticker['d'] = ticker['k'].rolling(K_t).mean()



apds = [mpf.make_addplot(ticker[['k','d']],  secondary_y=True, alpha=0.5, ylim=(-20,120)),
        mpf.make_addplot(ticker[['k','d']], panel=1),
]

fig, axes = mpf.plot(ticker, type='candle', addplot=apds, style='yahoo',
            figscale=1.1, figratio=(8,5),
            volume=True, volume_panel=2,
            panel_ratios=(6,3,2),  returnfig=True)
axes[1].legend(['k','d'], loc=2)
axes[2].legend(['k','d'], loc=2)
plt.show()
