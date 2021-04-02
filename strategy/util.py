import numpy as np

def moving_stop_loss(dw, stop_loss = 0.2):

    holding = 0
    high = 0
    if not 'sell' in dw:
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

def crossover(dw, i , a, b):
    if (((dw.iloc[i][a] > dw.iloc[i][b]) and (dw.iloc[i-1][a] < dw.iloc[i-1][b])) and (dw.iloc[i][a] > dw.iloc[i-1][a])):
        return 1;
