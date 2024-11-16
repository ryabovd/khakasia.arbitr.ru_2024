import datetime
import smtplib
import json
import time


def send_notification(text, subject, adress_list):
    email = adress_list
    with open('settings.json', 'r', encoding='utf-8') as file:
        settings = json.load(file)
        sender = settings["sender"]
        sender_password = settings["sender_password"]
    mail_lib = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
    mail_lib.login(sender, sender_password)
    for to_item in email:
        msg = 'From: %s\r\nTo: %s\r\nContent-Type: text/plain; charset="utf-8"\r\nSubject: %s\r\n\r\n' % (
            sender, to_item, '{}'.format(subject))
        msg += text
        mail_lib.sendmail(sender, to_item, msg.encode('utf8'))
        print('Отправлено письмо на адрес {}'.format(to_item))
        time.sleep(2)
    print('\n')
    mail_lib.quit()


def date_today():
    '''Func that returned today date'''
    today = datetime.date.today()
    return today