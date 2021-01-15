import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf

kd_n = 30
RSV_t = 10
K_t = 10

ticker = pd.read_csv('data/tejdb_20201216210131.csv', index_col = 'Date', parse_dates = True)
ticker['Volume'] = [int(i.replace(',', '')) for i in ticker['Volume']]
ticker.sort_index(inplace = True)

tmp = pd.DataFrame(index=ticker.index)
tmp['max_close'] = ticker['Close'].rolling(kd_n).max()
tmp['min_close'] = ticker['Close'].rolling(kd_n).min()
tmp['RSV'] = (ticker['Close'] - tmp['min_close'])/(tmp['max_close']-tmp['min_close'])*100

tmp['k'] = tmp['RSV'].rolling(RSV_t).mean()
tmp['d'] = tmp['k'].rolling(K_t).mean()


apds = [mpf.make_addplot(tmp[['k','d']], panel=1), ]

s  = mpf.make_mpf_style(base_mpf_style='yahoo',gridstyle='--')

fig, axes = mpf.plot(ticker, type='candle', addplot=apds, style=s,
            figscale=1.2, figratio=(8,5),
            volume=True, volume_panel=2,
            panel_ratios=(6,3,2),  returnfig=True, mav=(30,60))

axes[0].legend(['MA30','MA60'], loc=2)
axes[2].legend(['k','d'], loc=2)
plt.show()
