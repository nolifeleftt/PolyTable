from bs4 import BeautifulSoup
import requests
import datetime
import telebot
from telebot import types
import time
import subprocess
def parse(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    page = soup.find_all('li', class_='schedule__day')
    t = [[], [], [], [], [], [], []]
    i = 0
    for day in page:
        date = (day.find('div', class_='schedule__date').text.strip())
        t[i].append('🗓️' + date)
        lessons = day.find_all('li', class_='lesson')
        for lesson in lessons:
            t[i].append('🕰️' + lesson.find('div', class_='lesson__subject').text.strip() + ', ' + (
                lesson.find('div', class_='lesson__type').text.strip()))
            t[i].append('📌' + lesson.find('div', class_='lesson__places').find('div').text.strip() + '\n')
        i += 1
    return t

def get_url(id):
    ids = {}
    with open('ids.txt') as file:
        for i in file.readlines():
            key, val = i.strip().split(';')
            ids[key] = val
    url = ids[str(id)]
    if url.find('?') != -1:
        url = ids[str(id)][:url.find('?')]
    else:
        url = ids[str(id)]
    return url

def open_file(filename):
    ids = {}
    with open(filename) as file:
        for i in file.readlines():
            key, val = i.strip().split(';')
            ids[key] = val
    return ids
client = telebot.TeleBot('5741562885:AAE0B_c2HMWYTNS0HA_c1HnkJE4ttq7vTD4')
l = []
while True:
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    dt = datetime.datetime.today()
    if dt.hour == 18 and dt.minute ==30:
        d = open_file('ids.txt')
        for id in d:
            if today.isoweekday() == 5:
                client.send_message(id, "Завтра воскресенье!")
            else:
                t = parse(get_url(id))
                res = ' ' * 39 + '\n'.join(t[today.weekday() + 1]) + '\n' +' ' * 39
                client.send_message(id.strip(),'❗️Расписание на завтра:\n\n' + res.strip())
        time.sleep(60)
    elif dt.hour == 18 and dt.minute == 35:
        d = open_file('ids.txt')
        for id in d:
            if today.isoweekday() == 6:
                client.send_message(id, "Сегодня воскресенье!")
            else:
                t = parse(get_url(id))
                res = ' ' * 39 + '\n'.join(t[today.weekday()]) + '\n' + ' ' * 39
                client.send_message(id, '❗️Расписание на сегодня:\n\n' + res.strip())
        time.sleep(60)