import os
import glob
import pandas as pd
import csv

# 同フォルダのcsvファイルのリストを作成
csv_name_list = glob.glob('*.csv')

csv_list = []

# 各csvファイルのデータを読み取って
# リストに追加
for csv_name in csv_name_list:
    csv_list.append(pd.read_csv(csv_name))

# リストのデータを結合
merge_csv = pd.concat(csv_list)

# 結合したデータをcsvに出力
merge_csv.to_csv('horse_result.csv', encoding='utf_8', index=False)
