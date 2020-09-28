import json

import requests
from bs4 import BeautifulSoup


# Parse shop information from https://www.mebelshara.ru/contacts
def parse_mebelshara(html) -> str:
    shops_info = []
    bs_obj = BeautifulSoup(html, features="lxml")
    city_list = bs_obj.findAll("div", {"city-item"})
    for city in city_list:
        shop_list = city.findAll("div", {"shop-list-item"})
        for shop in shop_list:
            shop_info = {
                "address": city.h4.get_text() + ", " + shop.find("div", {"shop-address"}).get_text(),
                "latlon": [float(city.find("div", {"shop-list-item"})['data-shop-latitude']),
                           float(city.find("div", {"shop-list-item"})['data-shop-longitude'])],
                "name": shop.find("div", {"shop-name"}).get_text(),
                "phones": [phone for phone in shop.find("div", {"shop-phone"})],
                "working_hours": [work_time.get_text() for work_time in shop.find_all("div", {"shop-weekends"})]
            }
            shops_info.append(shop_info)

    return json.dumps(shops_info, ensure_ascii=False, indent=2)


def parse_tui(html):
    shops_info = []
    bs_obj = BeautifulSoup(html, features="lxml")
    print(html)


def main():
    session = requests.Session()
    session.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
        "Accept-Language": "ru-RU,ru-BY;q=0.9,ru;q=0.8,en-GB;q=0.7,en;q=0.6,be-BY;q=0.5,be;q=0.4,en-US;q=0.3"
    }
    mebelshara_url = "https://www.mebelshara.ru/contacts"
    tui_url = "https://www.tui.ru/offices/"
    print(parse_mebelshara(session.get(mebelshara_url).text))
    # parse_tui(requests.get(tui_url).text)


if __name__ == '__main__':
    main()
