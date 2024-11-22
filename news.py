from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import datetime
import json
import csv
from send_email import send_notification



def getHeader(url):
    try:
        html = urlopen(url)
    except HTTPError as e:
        return None
    try:
        bs = BeautifulSoup(html.read(), 'html.parser')
        header = bs.body.div.find('span', {'class': 'ac_name_first'})
    except AttributeError as e:
        return None
    return header


def getContainer(url):
    try:
        html = urlopen(url)
    except HTTPError as e:
        return None
    try:
        bs = BeautifulSoup(html.read(), 'html.parser')
        container = bs.div(attrs= {'class': 'info-box'}) 
    except AttributeError as e:
        return None
    return container


def getData(new):
    data = new.find('div', {'class': 'info-box__data'}).get_text()
    return data


def getNewText(new):
    newText = new.find('a').get_text()
    return newText


def getLink(new):
    newLink = new.find('a', href = True)['href']
    return newLink


def get_current_date(soup):
    current_date = soup[0].find('div', {'class': 'info-box__data'}).get_text()
    return current_date


def convert_date(date):
    date_list = date.split('.')
    year, month, day = int(date_list[2]), int(date_list[1]), int(date_list[0])
    return datetime.date(year, month, day)


def dates_diff(last_date, current_date):
    return convert_date(current_date) > convert_date(last_date)


def get_settings():
    with open('news_settings.json', 'r', encoding='utf-8') as file:
        settings = json.load(file)
    return settings


def save_news(news, CSV):
    with open(CSV, 'w', encoding='utf-8')  as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['Дата', 'Заголовок', 'Ссылка', 'Текст'])
        for news_dict in news:
            writer.writerow( [news_dict['news_date'], news_dict['news_title'], news_dict['news_link']] )


def get_news_from_contenteiner(container, last_date):
    news_list_dict = []
    for new in container:
        data = getData(new)
        if convert_date(last_date) < convert_date(data):
            new_text = getNewText(new)
            new_link = getLink(new)
            news_list_dict.append(
                {
                    'news_date': data,
                    'news_title': new_text,
                    'news_link': new_link
                }
            )
    return news_list_dict


def text_for_send(news):
    '''That func prepared text of message and add footer with add_footer func'''
    text = ''
    for news_dict in news:
        text += news_dict['news_date'] + '\n' + news_dict['news_title'] + '\n' + news_dict['news_link'] + '\n' + '\n'
    text += add_footer()
    return text


def add_footer():
    '''In that func contains text of message's footer.'''
    footer = '\nОТКАЗАТЬСЯ от получения рассылок ▼ \n\nmailto:dmitryabov@yandex.ru?subject=UNSUBSCRIBE&body=Не%20присылайте%20больше%20писем'
    return footer


def write_new_settings_json(settings):
    with open('news_settings.json', 'w', encoding='utf-8') as file:
        json.dump(settings, file, indent=4, ensure_ascii=False)


def get_adress_list(settings):
    adresses = settings['adress_list'].items()
    adress_list = []
    for _, v in adresses:
        adress_list.append(v)
    return adress_list


def get_name_court(soup):
    name_court = 'Арбитражный суд ' + soup.text
    return name_court    


def main():
    CSV = 'news_arbitr.ru.csv'
    container = getContainer('https://khakasia.arbitr.ru/news-isfb')
    if container == None:
        print('Container could not be found')
    else:
        header = getHeader('https://khakasia.arbitr.ru/news-isfb')
        court = get_name_court(header)
        settings = get_settings()
        last_date = settings['last_date']
        current_date = get_current_date(container)
        if dates_diff(last_date, current_date) == True:
            print('Есть НОВОСТИ')
            news = get_news_from_contenteiner(container, last_date)
            print('\nНовости получены')
            save_news(news, CSV)
            print('Новости сохранены')
            text = text_for_send(news)
            new_last_date = news[0]['news_date']
            subject = court + ' | Новости на ' + new_last_date
            adress_list = get_adress_list(settings)
            #send_notification(text, subject, adress_list)
            settings['last_date'] = new_last_date
            #write_new_settings_json(settings)
        else:
           print('Новости ОТСУТСТВУЮТ\n')
    print('Работа скрипта ЗАВЕРШЕНА\n')


if __name__ == "__main__":
    main()

# Переписать сохранение новостей в json
# Написать цикл для проверки судов Тывы и Красноярского края
# Написать проверку новостей не только по дате, но и по содержанию первой новости
# Написать вывод в консоль время выполнения скрипта
# Написать функцию для работы с аргументами строки (с какой даты, выводить в консоль, отправлять по почте)
# +Исправить функцию записи json, чтобы записывать красивые файлы
# Написать функцию проверки по расписанию ???
# +Переписать send_email.py, чтобы она брала список адресов из вне. Придумать где и как хранить список адресов или список адресов и фамилий
# +Сделать функцию проверки даты прошлой первой новости
# +Написать функцию записи новой даты новостей
# +Переписать скрипт на __main__
# +Написать функцию проверки даты последней новости, полученной при предыдущей проверке, и отбирающей только новые новости
# +Написать функцию отправки новостей по электронной почте
