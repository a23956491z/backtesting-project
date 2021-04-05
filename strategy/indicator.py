import pandas as pd
def KD(ticker,RSVn = 9,RSVt = 3,Kt = 3,):
    tmp = pd.DataFrame(index=ticker.index)

    # 以 RSVn 為區間，去取出最高收盤價
    tmp['max_close'] = ticker['Close'].rolling(RSVn).max()
    # 以 RSVn 為區間，去取出最低收盤價
    tmp['min_close'] = ticker['Close'].rolling(RSVn).min()

    # RSV的公式
    tmp['RSV'] = (ticker['Close'] - tmp['min_close'])/(tmp['max_close']-tmp['min_close'])*100

    # 以 RSVt 為區間，計算 RSV 的移動平均
    tmp['k'] = tmp['RSV'].rolling(RSVt).mean()

    # 以 Kt 為區間，計算 k 的移動平均
    tmp['d'] = tmp['k'].rolling(Kt).mean()

    return tmp['k'], tmp['d']
