from datetime import *
import requests
from time import sleep
import requests
from bs4 import BeautifulSoup
import json
import csv

from pycbrf import rates
from pycbrf import ExchangeRates, Banks

dollar = ''
eur = ''
funt = ''



url = 'https://cbr.ru/currency_base/daily/'
headers = {
    "accept": "*/*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 OPR/79.0.4143.73 (Edition Yx GX 03)"
}
all_val = {}

full_page = requests.get(url, headers=headers)
soup = BeautifulSoup(full_page.content, 'html.parser')
convert = soup.find(class_='data').findAll('th')
# print(convert)
number_cod = convert[0].text
letter_cod = convert[1].text
numb = convert[2].text
name_val = convert[3].text
kurs = convert[4].text
# print(kurs)

# with open(f"val.csv", "w", encoding="utf-8") as file:
#     writer = csv.writer(file)
#     writer.writerow(
#         (
#             number_cod,
#             letter_cod,
#             numb,
#             name_val,
#             kurs
#         )
#     )
# print(convert_val)
convert_2 = soup.find(class_='data').findAll('tr')
# print(convert_2)
for item in convert_2:
    try:
        convert_val = item.find_all('td')
        number_cod = convert_val[0].text
        letter_cod = convert_val[1].text
        numb = convert_val[2].text
        name_val = convert_val[3].text
        kurs = convert_val[4].text
        if name_val == 'Фунт стерлингов Соединенного королевства':
            funt = f'{name_val}: {kurs}'
        elif name_val == 'Доллар США':
            dollar = f'{name_val}: {kurs}'
        elif name_val == 'Евро':
            eur = f'{name_val}: {kurs}'

    except IndexError:
        pass

    # with open(f"val.csv", "a", encoding="utf-8") as file:
    #     writer = csv.writer(file)
    #     writer.writerow(
    #         (
    #             number_cod,
    #             letter_cod,
    #             numb,
    #             name_val,
    #             kurs
    #         )
    #     )
# print(funt)
# print(eur)
# print(dollar)

def get_money():
    req = requests.get('https://yobit.net/api/3/ticker/btc_usd')
    response = req.json()
    sell_price = response["btc_usd"]["sell"]
    return (f"{datetime.now().strftime('%Y/%m/%d %H:%M')}\nЦена продажи Биткоина: {round(sell_price, 2)} Долларов")


btc = (get_money())
