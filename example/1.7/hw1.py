
# %%
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import talib
import mplfinance as mpf

#pls use your data here
ticker = pd.read_csv('data/tejdb_20201214151755.csv', index_col = 'Date', parse_dates = True)
ticker = ticker.sort_index()
ticker = ticker.iloc[-150:]
#ticker['Volume'] = [int(v.replace(',', '')) for v in ticker['Volume'] ]

print(ticker)
# %%

#pls set the proper window of your data
short_window = 2
long_window = 5
dw = ticker
dw['slowk'], dw['slowd'] = talib.STOCH(
			ticker['High'].values,
			ticker['Low'].values,
			ticker['Close'].values,
                        fastk_period=short_window,
                        slowk_period=long_window,
                        slowk_matype=0,
                        slowd_period=long_window,
                        slowd_matype=0)

# %%

signals = pd.DataFrame(index=dw.index)
signals['signal'] = 0.0

signals['slowk'] = dw['slowk']
signals['slowd'] = dw['slowd']

signals['signal'][short_window:]  = np.where((signals['slowk'][short_window:]
                                            > signals['slowd'][short_window:]), 1.0, 0.0)
signals['positon'] = signals['signal'].diff()
signals['buy'] = np.where((signals['slowk'] > 80) & (signals['positon'] == 1 ), 1.0, 0.0)
signals['sell'] = np.where((signals['slowk'] < 20) & (signals['positon'] == -1 ), 1.0, 0.0)

print(signals['slowd'])
# %%


fig,axes = plt.subplots(3,1,figsize=(16,10))

#ticker[['Close']].plot(ax=axes[0], grid=True, title="yeah")

dw[['slowk','slowd']].plot(ax=axes[1], grid=True)

axes[1].plot(signals.loc[signals.buy == 1.0].index,
         signals.slowk[signals.buy == 1.0],
         '^', markersize=10, color='m', alpha=0.5)
axes[1].plot(signals.loc[signals.sell == 1.0].index,
         signals.slowk[signals.sell == 1.0],
         'v', markersize=10, color='k', alpha=0.5)

axes[2].bar(ticker.index, ticker['Volume'])
mpf.plot(ticker,type='candle', ax=axes[0])
plt.show()
