import pandas as pd
def KD(ticker,RSVn = 9,RSVt = 3,Kt = 3,):
    tmp = pd.DataFrame(index=ticker.index)
    tmp['max_close'] = ticker['Close'].rolling(RSVn).max()
    tmp['min_close'] = ticker['Close'].rolling(RSVn).min()
    tmp['RSV'] = (ticker['Close'] - tmp['min_close'])/(tmp['max_close']-tmp['min_close'])*100

    tmp['k'] = tmp['RSV'].rolling(RSVt).mean()
    tmp['d'] = tmp['k'].rolling(Kt).mean()

    return tmp['k'], tmp['d']
