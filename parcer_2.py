import requests
from bs4 import BeautifulSoup
import lxml
import csv
import json
import time
import os

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
}

url = input('Введите url страницы, которую хотите спарсить: ')

# os.mkdir('lamoda_pages')
# os.mkdir('data')

def get_all_pages():

    page = 1

    while True:
        req = requests.get(f'https://www.lamoda.ru/c/5289/clothes-odezhdadlyadomamuj/?page={page}', headers=headers)
        soup = BeautifulSoup(req.text, 'lxml')
        if soup.find('div', class_='products-list-item'):
            with open(f'lamoda_pages\\lamoda_page_{page}.html', 'w', encoding='utf-8') as file:
                file.write(req.text)
            print(f'Создана копия {page} страницы Lamoda!')
            page += 1
        else:
            print('Больше страниц нет! Предыдущая страница была последней!')
            print()
            break

    return page

def get_all_cards():
    page = 13
    all_cards_list = []
    for i in range(1, page+1):
        with open(f'lamoda_pages\\lamoda_page_{i}.html', 'r', encoding='utf-8') as file:
            src = file.read()
            soup = BeautifulSoup(src, 'lxml')
            card = soup.find_all('div', class_='products-list-item')
            all_cards_list.append(card)

        print(f'Спарсена {i} карточка продукта!')
        # time.sleep(1)
    print(all_cards_list)
    return (all_cards_list, page)

def get_content():
    content = get_all_cards()
    all_cards_list = content[0]
    last_page = content[1]
    result_list = []

    card_ = 1
    page = 1

    with open(r'data\result.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                'Тип одежды',
                'Бренд одежды',
                'Цена',
                'Скидка',
                'Ссылка на продукт'
            )
        )

    for card in all_cards_list:

        if page == last_page:
            print('*' * 20)
            print('Парсится последняя страница!')
            print('*' * 20)
        else:
            print('*' * 20)
            print(f'{page} из {last_page}')
            print('*' * 20)

        page += 1

        for item in card:
            if item.text.isspace():
                continue
            else:
                product_url = 'https://www.lamoda.ru' + item.find('a').get('href')
                product_brand_and_type = item.find('div', class_='products-list-item__brand').text.strip().split('\n')
                product_brand_and_type = [i.strip() for i in product_brand_and_type]
                product_brand = product_brand_and_type[0]
                product_type = product_brand_and_type[-1]
                price = item.find('span', class_='price').find_all('span')
                if len(price) == 3:
                    product_price = price[1].text.strip().replace(' ', '')
                    product_old_price = price[0].text.strip().replace(' ', '')
                    product_discont = f'{round(100 - (int(product_price) / int(product_old_price) * 100))}%'
                else:
                    product_price = price[0].text.strip().replace(' ', '')
                    product_discont = 'No discount'

                card_dict = {
                    'product_type': product_type,
                    'product_brand': product_brand,
                    'product_price': product_price,
                    'product_discont': product_discont,
                    'product_url': product_url
                }

                result_list.append(card_dict)

                print(f'{card_} карточка спарсена!')
                card_ += 1
                # time.sleep(1)

                with open(r'data\result.csv', 'a', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(
                        (
                            product_type,
                            product_brand,
                            product_price,
                            product_discont,
                            product_url
                        )
                    )

    print('Файл csv успешно создан!')
    print()

    with open(r'data\result.json', 'w', encoding='utf-8') as file:
        json.dump(result_list, file, indent=4, ensure_ascii=False)

    print('Файл json успешно создан!')
    print()

def main():
    get_content()

if __name__ == '__main__':
    main()