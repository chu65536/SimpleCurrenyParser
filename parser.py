import requests
import datetime
from datetime import date
from bs4 import BeautifulSoup


URL = 'http://www.cbr.ru/currency_base/daily/'
PERIOD = 90
TODAY = date.today()
DELTA = datetime.timedelta(days=1)


def get_html(url, params=None):
    r = requests.get(url, params=params)
    return r


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('td')

    data = []
    tmp = []
    k = 0
    for item in items:
        text = item.get_text()
        text = text.replace(',', '.')
        tmp.append(text)
        k += 1

        if k == 5:
            k = 0
            data.append({'num code': tmp[0],
                         'let code': tmp[1],
                         'rub num': tmp[2],
                         'currency': tmp[3],
                         'exchange rate': tmp[4]})
            tmp.clear()
    return data


def parse():
    html = get_html(URL)

    if html.status_code == 200:
        data = {}
        cur_date = TODAY
        for page in range(1, PERIOD + 1):
            print(f'Парсинг страницы {page} из {PERIOD} ...')

            readable_date = cur_date.strftime("%d.%m.%Y")
            html = get_html(URL, params={'UniDbQuery.Posted': 'True',
                                         'UniDbQuery.To': readable_date})
            data[f'{readable_date}'] = get_content(html.text)
            cur_date -= DELTA

        return data
    else:
        print('Error')


def solve():
    data = parse()
    mx = {}
    mn = {}
    average = {}

    for day in data:
        for i in data[day]:
            cur = i['currency']
            rate = float(i['exchange rate'])

            if cur in average:
                average[cur] += rate
            else:
                average[cur] = rate

            if cur in mx:
                if rate > mx[cur][0]:
                    mx[cur] = [rate, day]
            else:
                mx[cur] = [rate, day]

            if cur in mn:
                if rate < mn[cur][0]:
                    mn[cur] = [rate, day]
            else:
                mn[cur] = [rate, day]

    for currency in average:
        average[currency] /= PERIOD

    f = open('output.txt', 'w')
    f.write('Максимум по всем валютам: \n')
    for cur in mx:
        f.write(f'{cur}: {mx[cur][0]} | {mx[cur][1]}\n')
    f.close()

    f = open('output.txt', 'a')
    f.write('\n')
    f.write('Минимум по всем валютам: \n')
    for cur in mn:
        f.write(f'{cur}: {mn[cur][0]} | {mn[cur][1]}\n')

    f.write('\n')
    f.write('Средние значение по всем валютам: \n')
    for cur in average:
        f.write(f'{cur}: {"%.4f" % average[cur]}\n')
    f.close()

    print('Готово.')


solve()
