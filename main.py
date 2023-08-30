# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import datetime
import telebot
from telebot import types


def check_link(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    if soup.find('a', class_='switcher__link') != None:
        if soup.find('a', class_='switcher__link').text == 'Предыдущая неделя':
            return True
        else:
            return False

def open_file(filename):
    ids = {}
    with open(filename) as file:
        for i in file.readlines():
            key, val = i.strip().split(';')
            ids[key] = val
    return ids

def get_url(id, date):
    ids = {}
    with open('ids.txt') as file:
        for i in file.readlines():
            key, val = i.strip().split(';')
            ids[key] = val
    url = ids[str(id)] + f'?date={date}'
    return url

def parse(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    page = soup.find_all('li', class_='schedule__day')
    t = [[], [], [], [], [], [], []]
    i = 0
    for day in page:
        date = (day.find('div', class_='schedule__date').text.strip())
        t[i].append('🗓️' +'<b>' + date + '</b>')
        lessons = day.find_all('li', class_='lesson')
        for lesson in lessons:
            t[i].append('⏰' + lesson.find('div', class_='lesson__subject').text.strip() + ', ' + (
                lesson.find('div', class_='lesson__type').text.strip()))
            t[i].append('📌' + lesson.find('div', class_='lesson__places').find('div').text.strip() + '\n')
        i += 1
    return t


while True:
    today = datetime.date.today()
    print(today)
    def file_user_id(uid, link):
        # Открываем файл для записи
        file = open('ids.txt', 'a')
        # Записываем
        if link.find('?') != -1:
            file.write(str(uid) + ';' + str(link)[:str(link).find('?')] + '\n')
        else:
            file.write(str(uid) + ';' + str(link) + '\n')
        # Закрываем файл
        file.close()
    l = []
    dt = datetime.datetime.today()
    client = telebot.TeleBot('5741562885:AAE0B_c2HMWYTNS0HA_c1HnkJE4ttq7vTD4')

    @client.message_handler(commands=['start'])
    def begin(message):
        ids = open_file('ids.txt')
        if str(message.chat.id) not in ids:
            markup_reply = types.InlineKeyboardMarkup()
            btn_my_site = types.InlineKeyboardButton(text='Расписание', url='https://ruz.spbstu.ru')
            markup_reply.add(btn_my_site)
            msg = client.send_message(message.chat.id, 'Привет! Чтобы начать получать расписание, нужно передать ссылку на расписание своей группы.\n\n<i>Найти ее можно нажав на кнопку ниже или перейдя сюда</i>: https://ruz.spbstu.ru/ и указав свои институт, курс и группу.', reply_markup=markup_reply, parse_mode='HTML')
            client.register_next_step_handler(msg, register)
            client.send_message(message.chat.id,'После того, как скоприруешь ссылку отправь ее мне.', parse_mode='HTML')

        else:
            markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn_1 = types.KeyboardButton('Получить расписание')
            btn_2 = types.KeyboardButton('Настройки')
            markup_reply.add(btn_1, btn_2)
            client.send_message(message.chat.id, 'Меню', reply_markup=markup_reply)

    def register(message):
        ids = open_file('ids.txt')
        if 'ruz' in str(message.text).strip() and str(message.chat.id) not in ids:
            if check_link(message.text.split()[-1]):
                markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
                file_user_id(message.chat.id, message.text.split()[-1])
                file = open('users.txt', 'a')
                file.write(str(message.from_user.username) + '\n')
                file.close()
                client.send_message(440453234, message.from_user.username + ' ' + 'just registred!')
                print(message.from_user.username, 'just registred!')
                client.send_message(message.chat.id, '<i>Регистрация успешно завершена!</i>\n\n<i>Если вы указали не ту ссылку или хотите сменить группу, нажмите "Настройки" -> "Сбросить ссылку" и укажите новую ссылку.</i>\n\nЕсли вместо меню у вас по-прежнему клавиатура, <b>нажмите на квадрат рядом с кнопкой отправки сообщения:</b>', reply_markup=markup_reply,  parse_mode='HTML')
                client.send_photo(message.chat.id, open('btn.png', 'rb'));
                btn_1 = types.KeyboardButton('Получить расписание')
                btn_2 = types.KeyboardButton('Настройки')
                markup_reply.add(btn_1, btn_2)
                client.send_message(message.chat.id, 'Меню', reply_markup=markup_reply)
            else:
                markup_reply = types.InlineKeyboardMarkup()
                btn_my_site = types.InlineKeyboardButton(text='Расписание', url='https://ruz.spbstu.ru')
                markup_reply.add(btn_my_site)
                msg = client.send_message(message.chat.id, 'Неверная ссылка. Укажите правильную ссылку на расписание вашей группы', reply_markup=markup_reply)
                client.register_next_step_handler(msg, register)
        else:
            markup_reply = types.InlineKeyboardMarkup()
            btn_my_site = types.InlineKeyboardButton(text='Расписание', url='https://ruz.spbstu.ru')
            markup_reply.add(btn_my_site)
            msg = client.send_message(message.chat.id, 'Неверная ссылка. Укажите правильную ссылку на расписание вашей группы', reply_markup=markup_reply)
            client.register_next_step_handler(msg, register)
    @client.message_handler(content_types=['text'])
    def get_rasp(message):
        ids = open_file('ids.txt')
        if message.text == 'Получить расписание':
            if str(message.chat.id) in ids:
                markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn_1 = types.KeyboardButton('Расписание на сегодня')
                btn_2 = types.KeyboardButton('Расписание на завтра')
                btn_3 = types.KeyboardButton('Расписание на текущую неделю')
                btn_4 = types.KeyboardButton('Расписание на следующую неделю')
                btn_5 = types.KeyboardButton('Назад')
                markup_reply.add(btn_1, btn_2,btn_3, btn_4, btn_5)
                client.send_message(message.chat.id, 'На какой день прислать расписание?', reply_markup=markup_reply)
            else:
                markup_reply = types.InlineKeyboardMarkup()
                btn_my_site = types.InlineKeyboardButton(text='Сайт с расписанием', url='https://ruz.spbstu.ru')
                markup_reply.add(btn_my_site)
                msg = client.send_message(message.chat.id, 'У меня нет ссылки на ваше расписание.\nПожалуйста, пришлите мне ссылку на ваше расписание.', reply_markup=markup_reply , parse_mode='HTML')
                client.register_next_step_handler(msg, register)
        if message.text == 'Расписание на сегодня':
            today = datetime.date.today()
            if today.isoweekday() == 7:
                client.send_message(message.chat.id, "Сегодня воскресенье!")
            else:
                if str(message.chat.id) in ids:
                    t = parse(get_url(message.chat.id, today))
                    res = '\n'.join(t[today.weekday()])
                    client.send_message(message.chat.id, res, parse_mode='HTML')
                else:
                    markup_reply = types.InlineKeyboardMarkup()
                    btn_my_site = types.InlineKeyboardButton(text='Сайт с расписанием', url='https://ruz.spbstu.ru')
                    markup_reply.add(btn_my_site)
                    msg = client.send_message(message.chat.id, 'У меня нет ссылки на ваше расписание.\nПожалуйста, пришлите мне ссылку на ваше расписание.', reply_markup=markup_reply, parse_mode='HTML')
                    client.register_next_step_handler(msg, register)
        if message.text == 'Расписание на завтра':
            today = datetime.date.today()
            if today.isoweekday() == 6:
                client.send_message(message.chat.id, "Завтра воскресенье!")
            elif today.isoweekday() == 7:
                t = parse(get_url(message.chat.id, today) + '?date=' + str(today + datetime.timedelta(days=1)))
                res = ' ' * 39 + '\n'.join(t[0]) + '\n' + ' ' * 39
                client.send_message(message.chat.id, res, parse_mode='HTML')
            else:
                if str(message.chat.id) in ids:
                    t = parse(get_url(message.chat.id, today))
                    res = ' ' * 39 + '\n'.join(t[today.weekday() + 1]) + '\n' +' ' * 39
                    client.send_message(message.chat.id, res, parse_mode='HTML')
                else:
                    markup_reply = types.InlineKeyboardMarkup()
                    btn_my_site = types.InlineKeyboardButton(text='Сайт с расписанием', url='https://ruz.spbstu.ru')
                    markup_reply.add(btn_my_site)
                    msg = client.send_message(message.chat.id, 'У меня нет ссылки на ваше расписание.\nПожалуйста, пришлите мне ссылку на ваше расписание.', reply_markup=markup_reply, parse_mode='HTML')
                    client.register_next_step_handler(msg, register)

        if message.text == 'Расписание на текущую неделю':
            if str(message.chat.id) in ids:
                today = datetime.date.today()
                t = parse(get_url(message.chat.id, today))
                res =''
                for i in t:
                    res += '\n'.join(i)
                    if i != t[-1] and i != t[-2]:
                        res += '\n\n\n' #+ ' ' * 39 + '\n'
                client.send_message(message.chat.id, res, parse_mode='HTML')
            else:
                markup_reply = types.InlineKeyboardMarkup()
                btn_my_site = types.InlineKeyboardButton(text='Сайт с расписанием', url='https://ruz.spbstu.ru')
                markup_reply.add(btn_my_site)
                msg = client.send_message(message.chat.id, 'У меня нет ссылки на ваше расписание.\nПожалуйста, пришлите мне ссылку на ваше расписание.', reply_markup=markup_reply, parse_mode='HTML')
                client.register_next_step_handler(msg, register)
        if message.text == 'Расписание на следующую неделю':
            today = datetime.date.today()
            if str(message.chat.id) in ids:
                if today.isoweekday() == 7:
                    nxt = today + datetime.timedelta(days=8)
                    nxt_url = get_url(message.chat.id, nxt)
                else:
                    nxt = today + datetime.timedelta(days=7)
                    nxt_url = get_url(message.chat.id, nxt)
                nxt_week = parse(nxt_url)
                res = ''
                for i in nxt_week:
                    res += '\n'.join(i)
                    if i != nxt_week[-1] and i != nxt_week[-2]:
                        res += '\n\n\n'  # + ' ' * 39 + '\n'
                client.send_message(message.chat.id, res, parse_mode='HTML')
            else:
                markup_reply = types.InlineKeyboardMarkup()
                btn_my_site = types.InlineKeyboardButton(text='Сайт с расписанием', url='https://ruz.spbstu.ru')
                markup_reply.add(btn_my_site)
                msg = client.send_message(message.chat.id, 'У меня нет ссылки на ваше расписание.\nПожалуйста, пришлите мне ссылку на ваше расписание.', reply_markup=markup_reply, parse_mode='HTML')
                client.register_next_step_handler(msg, register)
        if message.text == 'Назад':
            markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn_1 = types.KeyboardButton('Получить расписание')
            btn_2 = types.KeyboardButton('Настройки')
            markup_reply.add(btn_1, btn_2)
            client.send_message(message.chat.id, 'Меню', reply_markup=markup_reply)
        if message.text == 'Настройки':
            markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn_1 = types.KeyboardButton('Сбросить ссылку')
            btn_2 = types.KeyboardButton('Обратная связь')
            btn_3= types.KeyboardButton('Назад')
            markup_reply.add(btn_1, btn_2, btn_3)
            client.send_message(message.chat.id, 'Настройки', reply_markup=markup_reply)
        if message.text == 'Сбросить ссылку':
            ids = open_file('ids.txt')
            if str(message.chat.id) in ids:
                ids.pop(str(message.chat.id))
                markup_reply = types.InlineKeyboardMarkup()
                btn_my_site = types.InlineKeyboardButton(text='Сайт с расписанием', url='https://ruz.spbstu.ru')
                markup_reply.add(btn_my_site)
                msg  = client.send_message(message.chat.id, 'Ссылка сброшена, <i>пришлите мне новую ссылку на расписание вашей группы</i>',reply_markup=markup_reply, parse_mode='HTML')
                client.register_next_step_handler(msg, register)
                file = open('ids.txt', 'w')
                for key, value in ids.items():
                    file.write(f'{key};{value}\n')
                file.close()
            else:
                markup_reply = types.InlineKeyboardMarkup()
                btn_my_site = types.InlineKeyboardButton(text='Сайт с расписанием', url='https://ruz.spbstu.ru')
                markup_reply.add(btn_my_site)
                msg = client.send_message(message.chat.id, 'Ссылка уже сброшена, <i>пришлите мне новую ссылку на расписание вашей группы</i>', reply_markup=markup_reply, parse_mode='HTML')
                client.register_next_step_handler(msg, register)
        if message.text == 'Обратная связь':
            markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn_1 = types.KeyboardButton('Связаться с нами')
            btn_2 = types.KeyboardButton('Сказать "спасибо"')
            btn_3 = types.KeyboardButton('Назад')
            markup_reply.add(btn_1, btn_2, btn_3)
            client.send_message(message.chat.id, 'Обратная связь', reply_markup=markup_reply)
        if message.text == 'Связаться с нами':
            client.send_message(message.chat.id, "Авторы проекта:\n@nolifeleftt\n@plutoshka\nПо всем вопросам, предложениям и замечаниям вы можете обращаться к нам, мы обязательно Вам поможем❤")
        if message.text == 'Сказать "спасибо"':
            client.send_message(message.chat.id, 'Если вы хотите поблагодарить авторов за проделанную работу, помочь с оплатой хостинга, поддержать развитие проекта или просто сказать спасибо, мы будем очень признательный любой поддержке!🥺❤️\n\nНаши реквизиты:\n2202 2022 4665 7088\n\nСпасибо за выбор нашего бота!')
    client.infinity_polling(timeout=10, long_polling_timeout=5)
