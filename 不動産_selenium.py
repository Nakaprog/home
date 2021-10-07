from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd


url = "https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&pc=30&smk=&po1=25&po2=99&shkr1=03&shkr2=03&shkr3=03&shkr4=03&rn=0005&ek=000517640&ra=013&cb=0.0&ct=10.0&md=01&et=9999999&mb=0&mt=9999999&cn=9999999&tc=0400101&fw2=" 

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get(url)
print(url)

content_urls = []

# １パージ目とそれ以降のページでは次のページに遷移するためのパスが異なっていた
# １ページ目だけ別に取り出し処理をする
contents = driver.find_elements_by_class_name("ui-text--midium")
time.sleep(1)
for content in contents:
    # css_selectorは検証のコピーからselectorコピーを使用
    content_url = content.find_element_by_css_selector("a").get_attribute("href")
    print(f"url:{content_url}")
    content_urls.append(content_url)

try:
    next_page = driver.find_element_by_css_selector("div.pagination.pagination_set-nav p a").get_attribute("href")
    #js-leftColumnForm > div.pagination_set > div.pagination.pagination_set-nav > p > a
    driver.get(next_page)
    print(f"next url{next_page}")
except:
    time.sleep(1)


while True:
    contents = driver.find_elements_by_class_name("ui-text--midium")
    time.sleep(1)
    for content in contents:
        # css_selectorは検証のコピーからselectorコピーを使用
        content_url = content.find_element_by_css_selector("a").get_attribute("href")
        print(f"url:{content_url}")
        content_urls.append(content_url)


    try:
        next_page = driver.find_element_by_css_selector("div.pagination.pagination_set-nav p:nth-child(3) a").get_attribute("href")
        #js-leftColumnForm > div.pagination_set > div.pagination.pagination_set-nav > p:nth-child(3) > a
        driver.get(next_page)
        print(f"next url{next_page}")
    except:
        break

columns = ["名前", "賃料(万円)", "管理費・共益費(円)", "敷金(万円)", "礼金(万円)", "所在地", "駅徒歩", "間取り", "専有面積(㎡)", "築年数", "階", "リンク"]
df = pd.DataFrame(columns=columns)

try:
    for room_url in content_urls:
        print(f"url={room_url}")
        time.sleep(1)
        driver.get(room_url)
        print(driver)

        room_name = driver.find_element_by_css_selector("div.section_h1-header h1").text

        # xpathのコピーは「完璧なxpathをコピー」でコピーする
        price = driver.find_element_by_xpath("//div[4]/div[3]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/span[1]").text
        # /html/body/div[4]/div[3]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/span[1]
        price = price.replace("万円", "")
        control_cost = driver.find_element_by_xpath("//div[4]/div[3]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/span[2]").text
        # /html/body/div[4]/div[3]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/span[2]
        control_cost = control_cost.replace("管理費・共益費: ", "").replace("円", "")
        deposit = driver.find_element_by_xpath("//div[4]/div[3]/div[2]/div[1]/div[1]/div[1]/div[1]/div[2]/span[1]").text
        # /html/body/div[4]/div[3]/div[2]/div[1]/div[1]/div[1]/div[1]/div[2]/span[1]
        deposit = deposit.replace("敷金: ", "").replace("万円", "")
        reward = driver.find_element_by_xpath("//div[4]/div[3]/div[2]/div[1]/div[1]/div[1]/div[1]/div[2]/span[2]").text
        # /html/body/div[4]/div[3]/div[2]/div[1]/div[1]/div[1]/div[1]/div[2]/span[2]
        reward = reward.replace("礼金: ", "").replace("万円", "")

        # AttributeError: 'list' object has no attribute 'text'[0].textなどとインデックスを指定する
        address = driver.find_elements_by_css_selector("table.property_view_table tbody tr:nth-child(1) td")[0].text
        access = driver.find_elements_by_css_selector("table.property_view_table tbody tr:nth-child(2) td")[0].text
        layout = driver.find_elements_by_css_selector("table.property_view_table tbody tr:nth-child(3) td:nth-child(2)")[0].text
        #js-view_gallery > div.l-property_view_table > table > tbody > tr:nth-child(3) > td:nth-child(2)
        area = driver.find_elements_by_css_selector("table.property_view_table tbody tr:nth-child(3) td:nth-child(4)")[0].text
        #js-view_gallery > div.l-property_view_table > table > tbody > tr:nth-child(3) > td:nth-child(4)
        area = area.replace("m2", "")
        age = driver.find_elements_by_css_selector("table.property_view_table tbody tr:nth-child(4) td:nth-child(2)")[0].text
        #js-view_gallery > div.l-property_view_table > table > tbody > tr:nth-child(4) > td:nth-child(2)
        age = age.replace("築", "").replace("年", "")
        floor = driver.find_elements_by_css_selector("table.property_view_table tbody tr:nth-child(4) td:nth-child(4)")[0].text
        #js-view_gallery > div.l-property_view_table > table > tbody > tr:nth-child(4) > td:nth-child(4)
        floor = floor.replace("階", "")
        url = room_url

        print(room_name)
        print(price)
        print(control_cost)
        print(deposit)
        print(reward)
        print(address)
        print(access)
        print(layout)
        print(area)
        print(age)
        print(floor)

        se = pd.Series([room_name, price, control_cost, deposit, reward, address, access, layout, area, age, floor, url], columns)
        df = df.append(se, ignore_index=True)

except:
    print("Error")

df.to_csv("渋谷_selenium.csv", index=None, encoding="utf_8")
driver.quit()