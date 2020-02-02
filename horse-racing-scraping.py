from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import time
import csv
import os

URL = 'https://db.netkeiba.com/?pid=race_search_detail'
YEAR = ('2015', '2016', '2017', '2018', '2019')

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
    place = chrome.find_element_by_id('check_Jyo_09')
    place.click()

    # フォームの要素取得
    form = chrome.find_element_by_css_selector('#db_search_detail_form form')

    time.sleep(3)

    # フォーム送信
    form.submit()


# HTMLを解析
def parse_data():

    tr_list = chrome.find_elements_by_css_selector('.race_table_01 tbody tr')

    save_list = []
    # trを順に保存
    for index, tr in enumerate(tr_list):
        result_row = []
        results = None

        # ヘッダーの場合
        if index == 0:
            # ファイルが存在する場合
            if os.path.exists('keiba.csv'):
                continue
            results = tr.find_elements_by_css_selector('th')
        else:
            results = tr.find_elements_by_css_selector('td')

        for result in results:

            # 空白文字、スペース、タブ、改行を削除してテキスト追加
            result_row.append(''.join(result.text.splitlines()))

        save_list.append(result_row)

    return save_list


# ファイル書き込み
def write_file(result_rows):
    with open('keiba.csv', 'a', encoding='utf-8', newline='') as f:
        csv_writer = csv.writer(f)
        # 書き込み
        csv_writer.writerows(result_rows)


if __name__ == '__main__':

    for i in range(len(YEAR)):

        # 検索ページ
        chrome.get(URL)

        # 検索
        send_from(YEAR[i], YEAR[i])

        page_index = 0

        while True:
            # データ解析
            result_rows = parse_data()
            # ファイル書き込み
            write_file(result_rows)

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
