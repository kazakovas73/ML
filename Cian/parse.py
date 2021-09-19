from capcha import parse_selenium

from selenium import webdriver
import numpy as np
import pandas as pd
import bs4
import requests
import re
import time
from fake_useragent import UserAgent
import xlsxwriter

def get_href_bs4(browser, pages_list, css_sel):
    res = []
    flag = True
    for page in pages_list:
        print("Page: " + str(page) + ", collecting hrfs")

        browser.get(f"https://www.cian.ru/cat.php?deal_type=rent&engine_version=2&offer_type=flat&p={page}&region=1&room1=1&room2=1&type=4")
        if flag:
            time.sleep(15)
            flag = False
        source = browser.page_source


        soup = bs4.BeautifulSoup(source, features="html.parser")
        links = [a['href'] for a in soup.select(css_sel)]
        res.extend(links)
        #print("Page: " + str(page) + ", hrfs collected")
    return res


def parse_page(browser):
    res = []
    flag = True

    df_links = pd.read_excel("cian_links.xlsx")
    href_list = df_links["link"].values
    flag_list = df_links["added"].values

    #href_list = ["https://www.cian.ru/rent/flat/263514781/"]
    #flag_list = 0

    df_data = pd.read_excel("cian_rent12.xlsx")

    regions = ["ЦАО", "САО", "СВАО", "ВАО", "ЮВАО", "ЮАО", "ЮЗАО", "ЗАО",
               "СЗАО", "ЗАО", "НАО", "ТАО"]

    for page in href_list:
        #print("Page: " + str(page) + ", collecting data")
        if df_links[df_links["link"] == page]["added"].values[0] == 0:
            continue

        browser.get(page)

        '''if flag:
            time.sleep(30)
            flag = False'''
        #time.sleep(2)
        source = browser.page_source

        soup = bs4.BeautifulSoup(source, features="html.parser")

        price = soup.find("span", {"itemprop": "price"})
        if price is not None:
            #price = int("".join(re.findall("\d+", price)))
            text = price.text.split()
            price = int(text[0] + text[1])
        else:
            price = None

        area = None
        floor = None
        year = None
        region = None
        adress = None

        fridge = 0
        tv = 0
        bath = 0
        conditioner = 0
        internet = 0
        washing_machine = 0
        dishwasher = 0
        furniture_in_rooms = 0
        furniture_in_kitchen = 0

        infos = soup.find_all("div", {"class": "a10a3f92e9--info--3XiXi"})
        if infos is not None:
            for info in infos:
                if "Общая" in info.text:
                    area = float(info.text.split()[0].replace(",", "."))
                if "Этаж" in info.text:
                    floor = int(info.text.split()[0])
                if "Построен" in info.text:
                    year = int(re.findall("\d+", info.text)[0])

        adress = soup.find_all("a", {"class": "a10a3f92e9--link--1t8n1 a10a3f92e9--address-item--1clHr"})
        if adress is not None:
            region = adress[1].text.split()[0]

        features = soup.find_all("li", {"data-name": "FeatureItem"})
        if features is not None:
            if features is not None:
                for feature in features:
                    if "Холодильник" in feature.text:
                        fridge = 1
                    if "Телевизор" in feature.text:
                        tv = 1
                    if "Ванна" in feature.text:
                        bath = 1
                    if "Кондиционер" in feature.text:
                        conditioner = 1
                    if "Интернет" in feature.text:
                        internet = 1
                    if "Стиральная машина" in feature.text:
                        washing_machine = 1
                    if "Посудомоечная машина" in feature.text:
                        dishwasher = 1
                    if "Мебель в комнатах" in feature.text:
                        furniture_in_rooms = 1
                    if "Мебель на кухне" in feature.text:
                        furniture_in_kitchen = 1

        '''res.append({"area": area, "floor": floor, "year": year, "region": region, "fridge": fridge,
                    "tv": tv, "bath": bath, "conditioner": conditioner, "internet": internet,
                    "washing_machine": washing_machine, "dishwasher": dishwasher,
                    "furniture_in_rooms": furniture_in_rooms, "furniture_in_kitchen": furniture_in_kitchen})'''
        df_data = df_data.append({"price": price, "area": area, "floor": floor, "year": year, "region": region, "fridge": fridge,
                    "tv": tv, "bath": bath, "conditioner": conditioner, "internet": internet,
                    "washing_machine": washing_machine, "dishwasher": dishwasher,
                    "furniture_in_rooms": furniture_in_rooms, "furniture_in_kitchen": furniture_in_kitchen}, ignore_index=True)

        df_data.to_excel("cian_rent12.xlsx")
        df_links.loc[df_links["link"] == page, "added"] = 0
        df_links.to_excel("cian_links.xlsx")

        print("Page: " + str(page) + ", data collected")

    #return res


def create_df(df_list):
    df = pd.DataFrame.from_dict(df_list, orient="columns")
    print(df.head())

    return df

def get_links_df(browser):
    #flats_href = get_href_bs4(browser, pages_list, "._93444fe79c--link--39cNw")
    #df_links = pd.DataFrame(columns=["link", "added"])
    #df_links["link"] = flats_href
    #df_links["added"] = 0
    #df_links.to_excel("cian_links.xlsx")
    pass

    #return flats_href


if __name__ == "__main__":

    '''# pages_list = np.arange(1, 55, 1)
    # pages_list = [1]

    # df_links = pd.read_excel("cian_links.xlsx")

    cols = ["area", "floor", "year", "region", "fridge",
            "tv", "bath", "conditioner", "internet",
            "washing_machine", "dishwasher",
            "furniture_in_rooms", "furniture_in_kitchen"]

    try:
        browser = webdriver.Chrome()

        df_cian = pd.DataFrame(columns=cols)
        parsed_data = parse_page(browser)

        # df_cian = create_df(parsed_data)
        df_cian.to_excel("cian_rent12.xlsx")

    finally:
        browser.quit()
        
            
            try:
        browser = webdriver.Chrome()
        parse_page(browser)
    finally:
        browser.quit()
        '''
    df_links = pd.read_excel("cian_links.xlsx")

    df_data = pd.read_excel("cian_rent12.xlsx")

    print(df_data[df_data['price'] < 10000]["region"])
