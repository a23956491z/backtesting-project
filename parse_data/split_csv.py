#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import pandas as pd
import re
import os

def unique(list1):

    # insert the list to the set
    list_set = set(list1)
    # convert the set to the list
    unique_list = (list(list_set))
    return unique_list

csv_file = 'data/all_in_one.csv'

df = pd.read_csv(csv_file, usecols=['證券代碼', "簡稱"], encoding='cp950', low_memory=False)

df = df.drop_duplicates()
path = os.path.join('./data/', "ticker_name.csv")
df.to_csv(path, index=False)

# ticker_name_list = df["證券代碼"].astype(str) + df["簡稱"]
# df.values.tolist()
#
#
ticker_list = unique(df["證券代碼"].astype(str))
print('ticker amount : ',len(ticker_list))

#
# ticker_name_list = unique(ticker_name_list)
# ticker_name_dic = {}
# for ticker, name in zip(ticker_list, ticker_name_list):
#
#     name_space_removed = name.replace(' ', '')
#     ticker_name_dic[ticker] = name_space_removed.replace(ticker, ticker + '_')
#     print("|{}|".format(ticker),ticker_name_dic[ticker])
#
# print(ticker_name_dic)
# print(len(ticker_name_list))


# for ticker in ticker_list:
#     df1 = df[df['證券代碼'].astype(str) == ticker]
#     print(df1)


#print(ticker_name_list)

df = pd.read_csv(csv_file, encoding='cp950', low_memory=False)

counter = 1

for value, x in df.groupby('證券代碼'):
    print("{}/{}, {}".format(counter, len(ticker_list), value))
    counter += 1

    p = os.path.join('./data/splited/', "{}.csv".format(value.replace(' ','')))
    x = x.drop(columns=['證券代碼', '簡稱'])
    x.to_csv(p, index=False)
