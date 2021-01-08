
# %%
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

# TEJ 6530 2020/08/01-2020/12/11
ticker = pd.read_csv('data/tejdb_20201214164506.csv', index_col = 'Date', parse_dates = True)

rsi_n = 14
rsi_upper_bound = 80
rsi_lower_bound = 30

rsi_list = []
buy_or_sell = []
for i in range(0, ticker.shape[0]):

    escape = False

    up, down = [], []
    for j in range(0, rsi_n):
        cur = i+j
        if cur >= ticker.shape[0]-1:
            escape = True
            break

        diff = ticker.iloc[cur]['Close'] - ticker.iloc[cur+1]['Close']

        if diff > 0:
            up.append(diff)
        else:
            down.append((diff))

    if escape:
        rsi = np.nan
    else:

        avg_up = sum(up)/len(up)
        avg_down = abs(sum(down)/len(down))
        rsi = 100 * avg_up / (avg_up + avg_down)

    if np.isnan(rsi):
        buy_or_sell.append(np.nan)
    elif rsi < rsi_lower_bound:
        buy_or_sell.append(-1)
    elif rsi > rsi_upper_bound:
        buy_or_sell.append(1)
    else:
        buy_or_sell.append(0)

    rsi_list.append(rsi)

ticker['RSI'] = rsi_list
ticker['Method'] = buy_or_sell

# %%

fig = plt.figure(figsize = (20,10))
ax1,ax2 = fig.add_subplot(211), fig.add_subplot(212)

ax1.plot(ticker.index, ticker['RSI'])
ax1.plot(ticker.index, np.linspace(rsi_upper_bound,rsi_upper_bound, ticker.shape[0]))
ax1.plot(ticker.index, np.linspace(rsi_lower_bound,rsi_lower_bound, ticker.shape[0]))
ax2.plot(ticker.index, ticker['Method'])

plt.gcf().autofmt_xdate()
