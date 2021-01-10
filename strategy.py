import pandas as pd
import talib
import numpy as np

RSVn = 9
RSVt = 3
Kt = 3
upperBound = 70
lowerBound = 30

stop_loss = 0.2
def moving_stop_loss(dw, stop_loss = 0.2):

    holding = 0
    high = 0
    dw['sell'] = np.zeros(dw.shape[0])
    for index, row in dw.iterrows():
        if row['buy'] == 1:
            holding = 1

        if holding:
            if row['Close'] < high*(1-stop_loss) :
                row['sell'] = 1

                #print('sell : ', row['Close'] ,'high : ', high)
                holding = 0
                high = 0
            high = max(row['Close'], high)
            #print(high)
    return dw


def KDBuy_KDSell(ticker):


    dw = ticker
    dw['slowk'], dw['slowd'] = talib.STOCH(
    			ticker['High'].values,
    			ticker['Low'].values,
    			ticker['Close'].values,
                            fastk_period=RSVn, #RSV day
                            slowk_period=RSVt,
                            slowk_matype=0.0,
                            slowd_period=Kt,
                            slowd_matype=0.0)


    signals = pd.DataFrame(index=dw.index)
    signals['signal'] = 0.0
    signals['slowk'] = dw['slowk']
    signals['slowd'] = dw['slowd']
    signals['signal'][RSVn:]  = np.where((signals['slowk'][RSVn:]
                                                > signals['slowd'][RSVn:]), 1.0, 0.0)
    signals['positon'] = signals['signal'].diff()
    signals['buy'] = np.where((signals['slowk'] > upperBound) & (signals['positon'] == 1 ), 1.0, 0.0)
    signals['sell'] = np.where((signals['slowk'] < lowerBound) & (signals['positon'] == -1 ), 1.0, 0.0)

    dw['buy'] = signals['buy']
    dw['sell'] = signals['sell']

    return dw

def KDBuy_stopLoss(ticker):

    dw = ticker
    dw['slowk'], dw['slowd'] = talib.STOCH(
    			ticker['High'].values,
    			ticker['Low'].values,
    			ticker['Close'].values,
                            fastk_period=RSVn,
                            slowk_period=RSVt,
                            slowk_matype=0.0,
                            slowd_period=Kt,
                            slowd_matype=0.0)


    signals = pd.DataFrame(index=dw.index)
    signals['signal'] = 0.0
    signals['slowk'] = dw['slowk']
    signals['slowd'] = dw['slowd']
    signals['signal'][RSVn:]  = np.where((signals['slowk'][RSVn:]
                                                > signals['slowd'][RSVn:]), 1.0, 0.0)

    signals['positon'] = signals['signal'].diff()
    signals['buy'] = np.where((signals['slowk'] > upperBound) & (signals['positon'] == 1 ), 1.0, 0.0)
    dw['buy'] = signals['buy']

    dw = moving_stop_loss(dw, 0.2)
    return dw


ma_window_short, ma_window_mid,ma_window_long = 5,15,30
def tripleMA_stopLoss(  ticker,
                ma_window_short = 7,
                ma_window_mid = 15,
                ma_window_long = 21,
                tolerence_interval = 7):
    def crossover(i , a, b):
        if (((dw.iloc[i][a] > dw.iloc[i][b]) and (dw.iloc[i-1][a] < dw.iloc[i-1][b])) and (dw.iloc[i][a] > dw.iloc[i-1][a])):
            return 1;
    dw = ticker
    dw['ma_short'] = dw['Close'].rolling(ma_window_short).mean()
    dw['ma_mid'] = dw['Close'].rolling(ma_window_mid).mean()
    dw['ma_long'] = dw['Close'].rolling(ma_window_long).mean()

    dw['buy'] = np.zeros(dw.shape[0])
    if dw.shape[0] > ma_window_long:

        last_cross_mid = tolerence_interval
        last_cross_long = tolerence_interval
        for i in range(ma_window_long, dw.shape[0]):

            if crossover(i, 'ma_short', 'ma_mid'):
                last_cross_mid = 0
            if crossover(i, 'ma_short', 'ma_long'):
                last_cross_long = 0

            if (crossover(i, 'ma_mid', 'ma_long') and
                last_cross_mid < tolerence_interval and
                last_cross_long < tolerence_interval) :

                dw['buy'][i] =  1
                #print(dw.index[i])
                last_cross_mid = tolerence_interval
                last_cross_long = tolerence_interval

            last_cross_mid = last_cross_mid+1
            last_cross_long = last_cross_long+1


    dw = moving_stop_loss(dw, 0.2)


    return dw


if __name__ == '__main__':
    from tools import readStock_excel
    import matplotlib.pyplot as plt
    import mplfinance as mpf


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

    print(dw)
    plot_MA(dw)

    #plot_KD(dw)
