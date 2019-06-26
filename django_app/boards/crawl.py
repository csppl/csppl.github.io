from selenium import webdriver
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
import time
import sys
import requests
import shutil
import os

# 참고: https://pypi.org/project/selenium/

# 브라우저 띄우고
def browser_on():
    # 게코 드라이버 주소!
    driver_path = r'C:\STUDY\geckodriver-v0.24.0-win64\geckodriver.exe'
    # 환경변수 PATH에 집어넣어 준다!
    sys.path.append(driver_path)

    options = webdriver.FirefoxOptions()
    # 브라우저 안뜨게 해준다~
    options.add_argument('--headless')
    # 사람처럼 보이게
    options.add_argument("disable-gpu")  # 가속 사용 x
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko')  # user-agent

    return webdriver.Firefox(executable_path=driver_path, options=options)


# href 수집하는 부분
def href_crawler(browser, category, page):
    shop_title_list = []
    shop_href_list = []
    img_src_list = []
    # 네이버 쇼핑 주소
    main_url = f'https://search.shopping.naver.com/search/all.nhn?query={category}&pagingIndex={page}&pagingSize=20&cat_id=&frm=NVSHATC'

    browser.get(main_url)
    # 페이지 가지고올 수 있게 최대 15초까지 기다림
    browser.implicitly_wait(15)

    # 네이버쇼핑 검색결과 HTML 페이지
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')

    goods_list = soup.select_one('ul.goods_list').find_all('div', {'class': 'info'})

    # 가격 리스트
    price_list = soup.select_one('ul.goods_list').find_all('span', {'class': 'num _price_reload'})
    price_list = [x.text.strip() for x in price_list]

    img_list = soup.select_one('ul.goods_list').find_all('div', {'class': 'img_area'})

    for i in range(len(goods_list)):
        # 쇼핑몰 리스트
        many_shop = goods_list[i].find('span', {'class': 'price'}).find('a')

        # img source 가져오기
        img_src_list.append(img_list[i].find('img', {'class': '_productLazyImg'}).get('data-original'))
        print(f'{i}...')
        if many_shop == None:
            # 그냥 하나의 링크만 있으면 제목과 제일 싼 링크 가져오기
            shop_title_list.append(goods_list[i].find('a').text.strip())
            shop_href_list.append(goods_list[i].find('a').attrs['href'])
        else:
            # 판매처있으면 제일 싼 링크
            if '판매처' in many_shop.text:
                shop_title_list.append(goods_list[i].find('a').text.strip())
                shop_detail = many_shop.attrs['href']
                # print(shop_detail)
                browser.get(shop_detail)
                browser.implicitly_wait(15)
                html = browser.page_source
                soup = BeautifulSoup(html, 'html.parser')
                shop_href_list.append(soup.select_one('div.price_area').find('a').attrs['href'])
            else:
                shop_title_list.append(goods_list[i].find('a').text.strip())
                shop_href_list.append(goods_list[i].find('a').attrs['href'])

    return shop_title_list, shop_href_list, img_src_list, price_list


# 이미지 스크린샷
def image_scrapping(href_list, filename, browser):
    for idx, href in enumerate(href_list):
        print(f'{idx + 1}/{len(href_list)} {filename} screent shot...')
        try:
            browser.get(href)
            browser.implicitly_wait(15)
            time.sleep(7)

            # from here http://stackoverflow.com/questions/1145850/how-to-get-height-of-entire-document-with-javascript
            js = 'return Math.max( document.body.scrollHeight, document.body.offsetHeight,  document.documentElement.clientHeight,  document.documentElement.scrollHeight,  document.documentElement.offsetHeight);'
            scrollheight = browser.execute_script(js)
            scrollheight = min(60000, scrollheight)
            scale = 0.8
            browser.execute_script(f'document.body.style.MozTransform = "scale({scale})";')
            time.sleep(2)

            slices = []
            offset = 0
            while offset < scrollheight:
                print(offset)
                browser.execute_script(f"window.scrollTo(0, {offset});")
                time.sleep(1)
                img = Image.open(BytesIO(browser.get_screenshot_as_png()))
                offset += img.size[1]
                slices.append(img)
                # print (f'{offset} / {scrollheight}')
                time.sleep(1)

            # PILLOW
            print("PILLOW FIGHT!")
            screenshot = Image.new('RGB', (slices[0].size[0], scrollheight))
            offset = 0
            for img in slices:
                screenshot.paste(img, (0, offset))
                offset += img.size[1]

            try:
                screenshot.save(os.getcwd() + f'{filename}')
                print(f"{filename} saved!")
            except Exception as e:
                print(e)
            time.sleep(3)
        except:
            print('error!')
            continue


# Thumbnail download code
def img_download(img_list):
    for idx, img_ in enumerate(img_list):
        r = requests.get(img_, stream=True, headers={'User-agent': 'Mozilla/5.0'})
        if r.status_code == 200:
            if idx % 10 == 0:
                print(f'{idx}....')
            with open(f'./imgs/{idx}.jpg', 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        else:
            print(r.status_code)


