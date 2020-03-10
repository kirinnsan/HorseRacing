from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import datetime
import re
import time
import csv
import os


URL = 'https://db.netkeiba.com/?pid=race_search_detail'
YEAR = ('2018', '2019')
# YEAR = ('2015', '2016', '2017', '2018', '2019')
CHECKBOX_PLACE = 'check_Jyo_09'
RETRY_COUNT = 3
CSV_HEADER = ['date',                # 日付'         # ↓レース情報↓
              'distance',            # 距離'
              'weather',             # 天候'
              'ground',              # 馬場'
              'ground_status',       # 馬場状態'
              'result_rank',         # 着順'         # ↓レース結果↓
              'frame_number',        # 枠番'
              'horse_number',        # 馬番'
              'horse_name',          # 馬名'
              'age',                 # 性齢'
              'loaf_weight',         # 斤量'
              'player',              # 騎手'
              'time',                # タイム'
              'margin',              # 着差'
              'time_param',          # タイム指数'
              'passage',             # 通過'
              'up',                  # 上り'
              'tansyo',              # 単勝'
              'popular',             # 人気'
              'weight',              # 馬体重'
              'training_time',       # 調教タイム'
              'stables_comment',     # 厩舎コメント
              'comment',             # 備考'
              'trainer',             # 調教師'
              'horse_owner',         # 馬主'
              'money'                # 賞金(万円)'
              ]

# Chromeオプションのオブジェクト作成
options = ChromeOptions()
# ヘッドレス設定
# options.add_argument('-headless')
# Chrome起動
chrome = Chrome(options=options)


# ページ検索
def send_from(start, end):
    # 期間のセレクトボックス取得(開始年)
    start_year = chrome.find_element_by_name('start_year')
    start_year.send_keys(start)

    # 期間のセレクトボックス取得(開始月)
    start_month = chrome.find_element_by_name('start_mon')
    start_month.send_keys('1')

    # # 期間のセレクトボックス取得(終了年)
    end_year = chrome.find_element_by_name('end_year')
    end_year.send_keys(end)

    # # 期間のセレクトボックス取得(終了年)
    end＿month = chrome.find_element_by_name('end_mon')
    end＿month.send_keys('12')

    # 競馬場のチェックボックス
    place = chrome.find_element_by_id(CHECKBOX_PLACE)
    place.click()

    # 表示件数
    show_list = chrome.find_element_by_name('list')
    show_list.send_keys('100')

    # フォームの要素取得
    form = chrome.find_element_by_css_selector('#db_search_detail_form form')

    time.sleep(3)

    # フォーム送信
    form.submit()


# レース情報を取得する
def parse_race_info():
    reace_info = chrome.find_element_by_css_selector(
        '.racedata.fc dd p diary_snap_cut span')
    split_data = reace_info.text.split('/')

    race_sub_result = chrome.find_element_by_css_selector(
        '.data_intro .smalltxt').text

    date_pattern = re.search(r"(\d+)年(\d+)月(\d+)日", race_sub_result)
    date = date_pattern.group(
        1) + '/' + date_pattern.group(2) + '/' + date_pattern.group(3)  # 日付

    regex = re.compile('\d+')
    distance = regex.findall(split_data[0])[0].strip()    # 距離
    weather = split_data[1].split(':')[1].strip()         # 天候
    ground = split_data[2].split(':')[0].strip()          # 馬場
    ground_status = split_data[2].split(':')[1].strip()   # 馬場状態

    race_info_list = []
    race_info_list.append(date)
    race_info_list.append(distance)
    race_info_list.append(weather)
    race_info_list.append(ground)
    race_info_list.append(ground_status)

    return race_info_list


# レース結果ページURLを取得する
def parse_race_result_url(file_name):

    # 検索結果テーブルの行全て取得
    tr_list = chrome.find_elements_by_css_selector('.race_table_01 tbody tr')

    race_result_url_list = []

    # レース結果のリンクを順にリストに追加
    for index in range(1, len(tr_list)):

        race_result_url = tr_list[index].find_elements_by_tag_name('td')[4].\
            find_element_by_tag_name('a').get_attribute('href')
        race_result_url_list.append(race_result_url)

    return race_result_url_list


# レース結果ページを解析する
def parse_race_result_data(url, save_file_name):

    result_race_data_list = []

    # ページの読み込み待ち時間(10秒)
    chrome.set_page_load_timeout(10)

    race_result_tr_list = None
    i = 0
    while i < RETRY_COUNT:
        try:
            # レース結果ページ読み込み
            chrome.get(url)
            time.sleep(3)
            race_result_tr_list = chrome.find_elements_by_css_selector(
                '.race_table_01.nk_tb_common tbody tr')
            break
        except TimeoutException:
            i = i + 1
            print('TimeoutException Retrying:{}'.format(i))

    if race_result_tr_list is None:
        print('Can not parase url:{}'.format(url))

    # レース情報を取得
    race_info_list = parse_race_info()

    # レース結果情報に処理
    for index, tr in enumerate(race_result_tr_list):
        result_row = []
        results = None
        # ヘッダーの場合
        if index == 0:
            # 保存ファイルが存在する または 保存するリストにヘッダが含まれる場合
            if os.path.exists(save_file_name) or CSV_HEADER in result_race_data_list:
                continue
            result_race_data_list.append(CSV_HEADER)
            continue
        else:
            results = tr.find_elements_by_css_selector('td')
        # レース情報
        for result in race_info_list:
            result_row.append(result)
        # レース結果
        for result in results:
            # 空白文字、スペース、タブ、改行を削除してテキスト追加
            result_row.append(''.join(result.text.splitlines()))
        result_race_data_list.append(result_row)

    return result_race_data_list


# テキストファイル書き込み
def write_file(url, file_name):
    with open(file_name, 'a', encoding='utf-8') as f:
        # 書き込み
        f.write('\n'.join(url)+'\n')


# csvファイル書き込み
def write_csv_file(result_rows, file_name):
    with open(file_name, 'a', encoding='utf-8', newline='') as f:
        csv_writer = csv.writer(f)
        # 書き込み
        csv_writer.writerows(result_rows)

# ファイル読み込み
def read_file(file_name):
    with open(file_name, 'r', encoding='utf-8', newline='') as f:
        return f.readlines()


# レース結果のurlをテキストファイルに保存する
def save_rece_result_url():

    for i in range(len(YEAR)):

        # 検索ページ
        chrome.get(URL)

        # 検索
        send_from(YEAR[i], YEAR[i])

        page_index = 0

        file_name = 'keiba_{}_{}_url.txt'.format('阪神', YEAR[i])

        while True:

            # データ解析
            race_result_url = parse_race_result_url(file_name)

            # ファイル書き込み
            write_file(race_result_url, file_name)

            next_page = chrome.find_elements_by_css_selector('.pager a')

            # 最終ページチェック
            if next_page[0].text == '前' and next_page[1].text == '前':
                break
            # 検索結果1ページ目の場合
            if page_index == 0:
                next_page[0].click()
            else:
                next_page[1].click()

            page_index += 1

            time.sleep(3)


# レース結果のcsvファイルを作成する
def make_csv_for_race_result():

    for i in range(len(YEAR)):
        file_name = 'keiba_{}_{}_url.txt'.format('阪神', YEAR[i])
        url_list = read_file(file_name)
        result_rows = None
        save_file_name = file_name.replace('_url.txt','.csv')
        for url in url_list:
            result_rows = parse_race_result_data(url, save_file_name)
            # 取得取得したレース情報をcsvファイルに書き込み
            write_csv_file(result_rows, save_file_name)


if __name__ == '__main__':

    # save_rece_result_url()

    make_csv_for_race_result()