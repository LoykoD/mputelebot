import requests
from bs4 import BeautifulSoup as BS

from db import BotDB

class Parsing:
    def __init__(self, db):
        #url = "https://mospolytech.ru/postupayushchim/programmy-obucheniya/"
        headers = {
            "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
        }
        for number_page in range(1, 15):
            url = "https://mospolytech.ru/postupayushchim/programmy-obucheniya/?AJAX=Y&TYPE%5B0%5D=1&SEARCH=&FACULTY=&PAGEN_1=" + str(
                number_page)
            req = requests.get(url, headers=headers)
            src = req.text
            soup = BS(src, 'lxml')
            all_find = soup.find_all(class_='card-program-list__item')
            for item in all_find:
                name_facult = item.find_next(class_='card-program__tag text-label').text
                name_napravl = item.find_next(class_='card-program__title text-bold').text
                html_item_budget = item.find_next(class_='card-program__info')
                count_budget = ''
                passing_score = ''
                for j in html_item_budget:
                    try:
                        chet = j.find(class_='numerical-item__label text-default').text
                        if chet == 'Проходной балл':
                            passing_score = str(
                                (j.find(class_='numerical-item__number text-fact-2')).text.strip().replace('\n', ' '))
                        elif chet == 'Бюджетных мест':
                            count_budget = str(
                                j.find(class_='numerical-item__number text-fact-2').text.strip().split()[0])
                    except Exception as ex:
                        pass

                if (name_facult == 'ФМ'):
                    name_facult = 'Факультет машиностроения'
                elif (name_facult == 'ФИТ'):
                    name_facult = 'Факультет информационных технологий'
                elif (name_facult == 'ИГрИК'):
                    name_facult = 'Институт графики и искусства книги имени В.А. Фаворского'
                elif (name_facult == 'ТФ'):
                    name_facult = 'Транспортный факультет'
                elif (name_facult == 'ФХТиБ'):
                    name_facult = 'Факультет химической технологии и биотехнологии'
                elif (name_facult == 'ФУиГХ'):
                    name_facult = 'Факультет урбанистики и городского хозяйства'
                elif (name_facult == 'ИИДиЖ'):
                    name_facult = 'Институт издательского дела и журналистики'
                try:
                    #BotDB.add_facults(db,name_facult) # Парсинг самих факультетов
                    BotDB.add_specdata(db, name_facult, name_napravl, passing_score, count_budget)
                except Exception as Ex:
                    print(Ex, name_facult)



