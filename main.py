import os
from selenium.webdriver import Chrome, ChromeOptions
import pandas as pd
import time
import datetime
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.webdriver import WebDriver

#Chromeを起動
def set_driver(driver_path, headless_flg):
    # Chromeドライバーの読み込み
    options = ChromeOptions()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    #return Chrome(executable_path=os.getcwd() + "/" + driver_path, options=options)
    return Chrome(ChromeDriverManager().install(), options=options)

def log(txt):
    now=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    logStr = f'[log: {now}] {txt}'
    # ログ出力
    with open(log_file_path, 'a', encoding='utf-8_sig') as f:
        f.write(logStr + '\n')
    print(logStr)

#以下メインコード
LOG_FILE_PATH = "log/log_{datetime}.log"
OUTPUT_CSV_PATH="./output_list_{search_keyword}_{datetime}.csv"
log_file_path=LOG_FILE_PATH.format(datetime=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))

if os.name == 'nt': #Windows
    driver = set_driver("chromedriver.exe", False)
elif os.name == 'posix': #Mac
    driver = set_driver("chromedriver", False)
driver.get("https://tenshoku.mynavi.jp/")
time.sleep(5)

try:
    # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')
    time.sleep(5)
    # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')
except:
    pass

search_keyword=input('検索ワードを入れてください >> ')
driver.find_element_by_class_name("topSearch__text").send_keys(search_keyword)
# 検索ボタンクリック
driver.find_element_by_class_name("topSearch__button").click()

num=1
success=0
fail=0
info_list = [['会社名','勤務地','給与','初年度年収']]
#3ページ分取得
for i in range(3):

    time.sleep(5)
    elems_list = driver.find_elements_by_class_name('cassetteRecruit')
    for elem in elems_list:
        try:
            info_list.append([])
            #会社名取得
            info_list[num].append(elem.find_element_by_class_name('cassetteRecruit__name').text)
            #勤務地取得
            info_list[num].append('None')
            trs=elem.find_elements_by_css_selector('tr')
            for tr in trs:
                if tr.find_element_by_css_selector('th').text == '勤務地':
                    info_list[num][1]=tr.find_element_by_css_selector('td').text
            #給与取得
            info_list[num].append('None')
            trs=elem.find_elements_by_css_selector('tr')
            for tr in trs:
                if tr.find_element_by_css_selector('th').text == '給与':
                    info_list[num][2]=tr.find_element_by_css_selector('td').text
            #初年度年収取得
            info_list[num].append('None')
            trs=elem.find_elements_by_css_selector('tr')
            for tr in trs:
                if tr.find_element_by_css_selector('th').text == '初年度年収':
                    info_list[num][3]=tr.find_element_by_css_selector('td').text
            success += 1
            log(f'{num}件目取得成功')
        except Exception as e:
            log(f'{num}件目取得失敗')
            log(e)
            fail += 1
        finally:
            num += 1

    driver.find_element_by_css_selector('.pager__next .iconFont--arrowLeft').click()

driver.quit()

#csvファイル出力
now=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
df = pd.DataFrame(info_list,columns=info_list[0])
df=df.drop(0)
df.to_csv(OUTPUT_CSV_PATH.format(search_keyword=search_keyword,datetime=now))

log('完了')