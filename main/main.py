import json
from time import sleep

import requests
from bs4 import BeautifulSoup


MEBELSHARA_URL = "https://www.mebelshara.ru/contacts"


# Parse html from https://www.mebelshara.ru/contacts
def parse_mebelshara(html):
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


# Generator return id of cities on tui.ru
def get_tui_cities():
    response = requests.get("https://apigate.tui.ru/api/office/cities")
    cities = json.loads(response.text).get('cities')
    for city in cities:
        yield city.get('cityId')


# Parse information using tui.ru API
def parse_tui():
    tui_offices = []
    file = open("tuiru.json", 'w')
    for cityId in get_tui_cities():
        response = requests.get(f"https://apigate.tui.ru/api/office/list?CityId={cityId}")
        offices = json.loads(response.text).get('offices')

        for office in offices:
            working_hours = []
            workdays = office.get('hoursOfOperation').get('workdays')
            saturday = office.get('hoursOfOperation').get('saturday')
            sunday = office.get('hoursOfOperation').get('sunday')

            if not workdays.get('isDayOff'):
                working_hours.append(f"пн - пт {workdays.get('startStr')} до {workdays.get('endStr')}")

            if not (saturday.get('isDayOff') and sunday.get('isDayOff')) and \
                    saturday.get('startStr') == sunday.get('startStr') and \
                    saturday.get('endStr') == sunday.get('endStr'):
                working_hours.append(f"cб - вс {saturday.get('startStr')} до {saturday.get('endStr')}")

            elif not saturday.get('isDayOff'):
                working_hours.append(f"cб {saturday.get('startStr')} до {saturday.get('endStr')}")

            elif not sunday.get('isDayOff'):
                working_hours.append(f"cб {sunday.get('startStr')} до {sunday.get('endStr')}")

            office_info = {
                'address': office.get('address'),
                'latlon': [office.get('latitude'), office.get('longitude')],
                'name': office.get('name'),
                'phones': [phone.get('phone').strip() for phone in office.get('phones')],
                'working_hours': working_hours
            }

            tui_offices.append(office_info)

        sleep(0.5)

    return json.dumps(tui_offices, ensure_ascii=False, indent=2)


# Write data to json file
def write_json(file_name, data):
    with open(file_name, 'w', encoding="utf-8") as file:
        file.write(data)


def main():
    write_json("mebelshara.json", parse_mebelshara(requests.get(MEBELSHARA_URL).text))
    write_json("tuiru.json", parse_tui())


if __name__ == '__main__':
    main()
