import pandas as pd
import talib
import numpy as np

from . import indicator, util

stop_loss = 0.2
"""
只使用KD指標作為買入賣出的判斷
高點線以上黃金交叉就買入
地點線以下死亡交叉就賣出
參數：
    ticker 股價 dataframe
    RSVn RSV計算最高股價與最低股價取幾天為區間
    RSVt 計算K時，平滑RSV(移動平均) 取幾天為區間
    Kt 計算D時，平滑K(移動平均) 取幾天為區間
    upperBound KD高於這個點就買入
    lowerBound KD低於這個點就賣出
    short_stop_loss 移動停損率
"""
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

    # positon 是 1 便是 k 向上穿出 d
    #           -1則是 k 向下穿出 d
    # 這裡的黃金與死亡交叉定義比較寬鬆
    # 不限定 k或d 一定要往上或往下
    dw['positon'] = dw['signal'].diff()

    # k 向上穿出並大於高點線就買入
    dw['buy'] = np.where((dw['slowk'] > upperBound) & (dw['positon'] == 1 ), 1.0, 0.0)

    # 是否進行移動停損
    if short_stop_loss:
        dw = util.moving_stop_loss(dw, 0.2)
    else :

        # k 向下穿出並小於低點線就賣出
        dw['sell'] = np.where((dw['slowk'] < lowerBound) & (dw['positon'] == -1 ), 1.0, 0.0)

    return dw

"""
使用三條均線進行判斷
產生金三角就買入
賣出則只使用移動停損
參數：
    ticker 股價 dataframe
    ma_window_short 第一條均線的區間
    ma_window_mid   第二條均線的區間
    ma_window_long  第三條均線的區間
    tolerence_interval  金三角的容許範圍
"""
def tripleMA_stopLoss(  ticker,
                ma_window_short = 7,
                ma_window_mid = 15,
                ma_window_long = 21,
                tolerence_interval = 7):

    dw = ticker

    # 計算三條平均線
    dw['ma_short'] = dw['Close'].rolling(ma_window_short).mean()
    dw['ma_mid'] = dw['Close'].rolling(ma_window_mid).mean()
    dw['ma_long'] = dw['Close'].rolling(ma_window_long).mean()

    # 初始化 買入信號的欄位
    dw['buy'] = np.zeros(dw.shape[0])
    if dw.shape[0] > ma_window_long:

        # 上一次 短線向上穿出中線 距離現在幾天
        last_cross_mid = tolerence_interval
        # 上一次 短線向上穿出長線 距離現在幾天
        last_cross_long = tolerence_interval
        for i in range(ma_window_long, dw.shape[0]):

            if util.crossover(dw, i, 'ma_short', 'ma_mid'):
                last_cross_mid = 0
            if util.crossover(dw, i, 'ma_short', 'ma_long'):
                last_cross_long = 0

            # 容許範圍內，短線是否向上穿出中線，短線是否向上穿出長線
            # 如果都有，且中線也向上穿出長線
            # 就判斷為金三角
            if (util.crossover(dw, i, 'ma_mid', 'ma_long') and
                last_cross_mid < tolerence_interval and
                last_cross_long < tolerence_interval) :

                # 金三角買入
                dw['buy'][i] =  1

                # 重置上一次短線穿出 距離現在幾天
                last_cross_mid = tolerence_interval
                last_cross_long = tolerence_interval

            last_cross_mid = last_cross_mid+1
            last_cross_long = last_cross_long+1

    # 賣出信號 僅使用移動停損
    dw = util.moving_stop_loss(dw, 0.2)
    return dw

"""
使用威廉指標進行判斷
會先判斷股價是否是近期最高點
如果是的話，低於低點線會買入
如果不是的話，高於高點線賣出
參數：
    ticker 股價 dataframe
    n 威廉指標的計算區間
    tolerence_interval 近期最高點的判斷天數
    lowerBound 低點線
    upperBound 高點線
    short_stop_loss 移動停損率
"""
def WMR(ticker, n = 14, tolerence_interval = 4, upperBound = 80, lowerBound = 20, short_stop_loss = True):
    dw = ticker

    # n 天內最高收盤價
    dw['current_high'] = dw['Close'].rolling(n).max()
    # n 天內最低收盤價
    dw['current_low'] = dw['Close'].rolling(n).min()

    # 威廉指標
    dw['W%R'] = (dw['current_high'] - dw['Close'])/(dw['current_high']-dw['current_low'])*100

    # tolerence_interval 期間內最高收盤價
    dw['HIGH_current_high'] =  dw['High'].rolling(tolerence_interval).max()

    # 是近期最高，且低於地點線，買入
    dw['buy'] = np.where((dw['W%R'] < lowerBound) & (dw['High'] == dw['HIGH_current_high'] ), 1.0, 0.0)

    # 是否進行移動停損
    if short_stop_loss:
        dw = util.moving_stop_loss(dw, 0.2)
    else :

        # 不是近期最高，且高於高點線，賣出
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
