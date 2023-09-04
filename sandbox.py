# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import datetime
import telebot
from telebot import types


url = 'https://ruz.spbstu.ru/faculty/100/groups/37297?date=2023-09-11'
response = requests.get(url)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'lxml')
page = soup.find_all('li', class_='schedule__day')
t = [[], [], [], [], [], [], []]
i = 0
for day in page:
    date = (day.find('div', class_='schedule__date').text.strip())
    t[i].append('🗓️' + '<b>' + date + '</b>')
    lessons = day.find_all('li', class_='lesson')
    for lesson in lessons:
        try:
            print((lesson.find('div', class_='lesson__teachers').find_all('span')[-1]).text)
        except AttributeError:
            pass
        # print(lesson)
        #t[i].append('⏰' + lesson.find('div', class_='lesson__subject').text.strip() + ', ' + (
        #    lesson.find('div', class_='lesson__type').text.strip()))
      # t[i].append('📌' + lesson.find('div', class_='lesson__places').find('div').text.strip() + '\n')
        # t[i].append('👨‍🏫' + lesson.find('div', class_='lesson__teachers').find_all('span')[-1].text.strip())
   # i += 1