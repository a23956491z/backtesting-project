import pandas as pd
import talib
import numpy as np

from . import indicator, util

stop_loss = 0.2
def pure_KD(ticker, RSVn = 9,
                        RSVt = 3,
                        Kt = 3,
                        upperBound = 70,
                        lowerBound = 30,
                        short_stop_loss=True,
                        internal_indicator = True):

    dw = ticker

    if internal_indicator:
        dw['slowk'], dw['slowd'] = indicator.KD(ticker, RSVn, RSVt, Kt)
    else:
        dw['slowk'], dw['slowd'] = talib.STOCH(
        			ticker['High'].values,
        			ticker['Low'].values,
        			ticker['Close'].values,
                                fastk_period=RSVn, #RSV day
                                slowk_period=RSVt,
                                slowk_matype=0.0,
                                slowd_period=Kt,
                                slowd_matype=0.0)

    dw['signal'] = 0.0
    dw['signal'][RSVn:]  = np.where((dw['slowk'][RSVn:]
                                                > dw['slowd'][RSVn:]), 1.0, 0.0)
    dw['positon'] = dw['signal'].diff()
    dw['buy'] = np.where((dw['slowk'] > upperBound) & (dw['positon'] == 1 ), 1.0, 0.0)

    if short_stop_loss:
        dw = util.moving_stop_loss(dw, 0.2)
    else :
        dw['sell'] = np.where((dw['slowk'] < lowerBound) & (dw['positon'] == -1 ), 1.0, 0.0)

    return dw

def tripleMA_stopLoss(  ticker,
                ma_window_short = 7,
                ma_window_mid = 15,
                ma_window_long = 21,
                tolerence_interval = 7):


    dw = ticker
    dw['ma_short'] = dw['Close'].rolling(ma_window_short).mean()
    dw['ma_mid'] = dw['Close'].rolling(ma_window_mid).mean()
    dw['ma_long'] = dw['Close'].rolling(ma_window_long).mean()

    dw['buy'] = np.zeros(dw.shape[0])
    if dw.shape[0] > ma_window_long:

        last_cross_mid = tolerence_interval
        last_cross_long = tolerence_interval
        for i in range(ma_window_long, dw.shape[0]):

            if util.crossover(dw, i, 'ma_short', 'ma_mid'):
                last_cross_mid = 0
            if util.crossover(dw, i, 'ma_short', 'ma_long'):
                last_cross_long = 0

            if (util.crossover(dw, i, 'ma_mid', 'ma_long') and
                last_cross_mid < tolerence_interval and
                last_cross_long < tolerence_interval) :

                dw['buy'][i] =  1
                #print(dw.index[i])
                last_cross_mid = tolerence_interval
                last_cross_long = tolerence_interval
            last_cross_mid = last_cross_mid+1
            last_cross_long = last_cross_long+1

    dw = util.moving_stop_loss(dw, 0.2)
    return dw

def WMR(ticker, n = 14, tolerence_interval = 4, upperBound = 80, lowerBound = 20, short_stop_loss = True):
    dw = ticker

    dw['current_high'] = dw['Close'].rolling(n).max()
    dw['current_low'] = dw['Close'].rolling(n).min()
    dw['W%R'] = (dw['current_high'] - dw['Close'])/(dw['current_high']-dw['current_low'])*100

    dw['HIGH_current_high'] =  dw['High'].rolling(tolerence_interval).max()

    dw['W%R_current_high'] =  dw['W%R'].rolling(tolerence_interval).max()
    dw['W%R_current_low'] =  dw['W%R'].rolling(tolerence_interval).min()

    dw['buy'] = np.where((dw['W%R'] < lowerBound) & (dw['High'] == dw['HIGH_current_high'] ), 1.0, 0.0)


    if short_stop_loss:
        dw = util.moving_stop_loss(dw, 0.2)
    else :
        dw['sell'] = np.where((dw['W%R'] > upperBound) & (dw['High'] != dw['HIGH_current_high']  ), 1.0, 0.0)


    return dw


if __name__ == '__main__':
    from tools import readStock_excel
    import matplotlib.pyplot as plt
    import mplfinance as mpf

    ma_window_short = 7
    ma_window_mid = 15
    ma_window_long = 21
    def plot_KD(dw):
        dw.index = pd.to_datetime(dw.index)

        fig,axes = plt.subplots(3,1,figsize=(16,10))

        dw[['slowk','slowd']].plot(ax=axes[1], grid=True)

        axes[1].plot(dw.loc[dw.buy == 1.0].index,
                 dw.slowk[dw.buy == 1.0],
                 '^', markersize=10, color='m', alpha=0.5)
        axes[1].plot(dw.loc[dw.sell == 1.0].index,
                 dw.slowk[dw.sell == 1.0],
                 'v', markersize=10, color='k', alpha=0.5)

        axes[2].bar(ticker.index, ticker['Volume'])
        mpf.plot(ticker,type='candle', ax=axes[0])
        plt.show()

    def plot_MA(dw):
        mpf.plot(dw, type='candle' ,mav=(ma_window_short, ma_window_mid,ma_window_long))


    ticker = readStock_excel('data/2327.xlsx')

    dw = tripleMA_stopLoss(ticker)
    plot_MA(dw)
    print(dw.to_string())

    #plot_KD(dw)
