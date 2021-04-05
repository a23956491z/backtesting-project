import numpy as np

# 移動停損
# stop_loss 低於股價最高點多少比例就賣出
def moving_stop_loss(dw, stop_loss = 0.2):

    holding = 0 # 是否有持股
    high = 0 # 股票最高點

    # 如果沒有賣出信號這個欄位便新增
    if not 'sell' in dw:
        dw['sell'] = np.zeros(dw.shape[0])


    for index, row in dw.iterrows():
        if row['buy'] == 1:
            holding = 1


        # 持股時會持續記錄最高收盤價
        # 並判斷是否要賣出
        if holding:
            # 低於最高收盤價一定比例
            # 就產生賣出信號
            if row['Close'] < high*(1-stop_loss) :
                row['sell'] = 1

                holding = 0
                high = 0

            high = max(row['Close'], high)

    return dw

# 線a 是否在第 i 天向上穿出線b
def crossover(dw, i , a, b):
    if (((dw.iloc[i][a] > dw.iloc[i][b]) and
        (dw.iloc[i-1][a] < dw.iloc[i-1][b])) and
        (dw.iloc[i][a] > dw.iloc[i-1][a])):

        return 1;
