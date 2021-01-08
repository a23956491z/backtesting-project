
# %%
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import talib
import mplfinance as mpf

#2387 from 20200601 to 20210105
ticker = pd.read_csv('data/price_2387_20200601-20210105.csv',
						index_col = 'Date',
						parse_dates = True)
holding_csv = pd.read_csv('data/2387_20200601-20210105.csv',
						index_col = 'Date',
						parse_dates = True)
ticker['holding'] = [float(v.replace(',','')) for v in holding_csv['投信持股數市值(百萬)']]

ticker = ticker.sort_index()

# %%

signals = pd.DataFrame(index=ticker.index)
signals['signal'] = 0.0

signals['holding'] = ticker['holding']


signals['signal'] = np.where( ticker['holding'] >= 300, 1.0, 0.0)
signals['positon'] = signals['signal'].diff()
signals['buy'] = np.where((signals['positon'] == 1 ), 1.0, 0.0)

signals['signal'] = np.where( (ticker['holding'] >= 1300) | (ticker['holding'] <= 200), 1.0, 0.0)
signals['positon'] = signals['signal'].diff()
signals['sell'] = np.where((signals['positon'] == 1 ), 1.0, 0.0)

signals['signal'] = [1 if i==1 else (-1 if j == 1 else 0)
 					for i,j in zip(signals['buy'], signals['sell'])]
# %%


fig,axes = plt.subplots(4,1,figsize=(16,10))

ticker[['holding']].plot(ax=axes[1], grid=True)

axes[1].plot(signals.loc[signals.buy == 1.0].index,
         signals.holding[signals.buy == 1.0],
         '^', markersize=10, color='m', alpha=0.5)
axes[1].plot(signals.loc[signals.sell == 1.0].index,
         signals.holding[signals.sell == 1.0],
         'v', markersize=10, color='k', alpha=0.5)

axes[2].bar(ticker.index, ticker['Volume'])
signals[['signal']].plot(ax=axes[3], grid=True)


mpf.plot(ticker,type='candle', ax=axes[0])
plt.show()
