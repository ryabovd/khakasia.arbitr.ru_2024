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


def date_today():
    '''Func that returned today date'''
    today = datetime.date.today()
    #print('today', type(today))
    #print(str(today.day) + '.' + str(today.month) + '.' + str(today.year))
    today_format = str(today.day) + '.' + str(today.month) + '.' + str(today.year)
    return today_format


def main():
    courts_dict = {
        'Арбитражный суд Республики Хакасия': 'https://khakasia.arbitr.ru/news-isfb',
        'Арбитражный суд Республики Тыва': 'https://tyva.arbitr.ru/news-isfb',
        'Третий арбитражный апелляционный суд': 'https://3aas.arbitr.ru/news-isfb',
        'Арбитражный суд Восточно-Сибирского округа': 'https://fasvso.arbitr.ru/news-isfb'
    }
    CSV = 'news_arbitr.ru.csv'
    for court, webpage in courts_dict.items():
        container = getContainer(webpage)
        if container == None:
            print('Container could not be found')
        else:
            #header = getHeader(webpage)
            court_name = court
            settings = get_settings()
            last_date = settings['last_date']
            current_date = get_current_date(container)
            if dates_diff(last_date, current_date) == True:
                print(court_name, 'Есть НОВОСТИ')
                news = get_news_from_contenteiner(container, last_date)
                print('Новости получены')
                save_news(news, CSV)
                print('Новости сохранены\n')
                text = text_for_send(news)
                new_last_date = news[0]['news_date']
                subject = court_name + ' | Новости на ' + new_last_date
                adress_list = get_adress_list(settings)
                send_notification(text, subject, adress_list)
            else:
                print(court_name, 'Новости ОТСУТСТВУЮТ\n')
    # print('date_today()', date_today())            
    # print('str(date_today())', str(date_today()))
    # print('convert_date(str(date_today())', convert_date(str(date_today())))
    settings['last_date'] = date_today()
    write_new_settings_json(settings)
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
