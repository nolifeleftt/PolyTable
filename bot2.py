# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import datetime
import telebot
from telebot import types

def parse_day(url, data):
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    page = soup.find_all('li', class_='schedule__day')
    t = []
    for day in page:
        date = day.find('div')
        if str(date.text[:2]) == str(data.strftime("%d")):
            t.append('🗓️' + '<b>' + date.text + '</b>')
            lessons = day.find_all('li', class_='lesson')
            for lesson in lessons:
                t.append('⏰' + lesson.find('div', class_='lesson__subject').text.strip() + ', ' + (
                    lesson.find('div', class_='lesson__type').text.strip()))
                t.append('📌' + lesson.find('div', class_='lesson__places').find('div').text.strip() + '\n')
    if not t:
        res = f"<i>На {data} занятий нет.</i>"
    else:
        res = ' ' * 39 + '\n'.join(t) + '\n' + ' ' * 39
    return res

def open_file(filename):
    contents = {}
    with open(filename) as file:
        for i in file.readlines():
            key, val = i.strip().split(';')
            contents[key] = val
    return contents

def get_url(id, date):
    ids = {}
    with open('ids.txt') as file:
        for i in file.readlines():
            key, val = i.strip().split(';')
            ids[key] = val
    url = 'https://ruz.spbstu.ru/faculty/100/groups/' + ids[str(id)] + f'?date={date}'
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
        t[i].append('🗓️' + '<b>' + date + '</b>')
        lessons = day.find_all('li', class_='lesson')
        for lesson in lessons:
            t[i].append('⏰' + lesson.find('div', class_='lesson__subject').text.strip() + ', ' + (
                lesson.find('div', class_='lesson__type').text.strip()))
            t[i].append('📌' + lesson.find('div', class_='lesson__places').find('div').text.strip() + '\n')
        i += 1
    return t

bot = telebot.TeleBot('5741562885:AAE0B_c2HMWYTNS0HA_c1HnkJE4ttq7vTD4')
today = datetime.date.today()
print(today)
def file_user_id(uid, group):
    # Открываем файл для записи
    file = open('ids.txt', 'a')
    # Записываем
    file.write(str(uid) + ';' + str(group) + '\n')
    # Закрываем файл
    file.close()


@bot.message_handler(commands=['start'])
def begin(message):
    ids = open_file('ids.txt')
    if str(message.chat.id) not in ids:
        msg = bot.send_message(message.chat.id,
                                  'Привет! Чтобы начать получать расписание, пришли мне номер своей группы.\n<i>Например, 3733805/10003</i>', parse_mode='HTML')
        bot.register_next_step_handler(msg, register)

    else:
        keyboard = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text="На сегодня", callback_data="today")
        callback_button_2 = types.InlineKeyboardButton(text="На завтра", callback_data="tomorrow")
        callback_button_3 = types.InlineKeyboardButton(text="На эту неделю", callback_data="week")
        callback_button_4 = types.InlineKeyboardButton(text="На следующую неделю", callback_data="nxtweek")
        keyboard.add(callback_button, callback_button_2, callback_button_3, callback_button_4)
        bot.send_message(message.chat.id, "На какой день прислать расписание?", reply_markup=keyboard)
def register(message):
    ids = open_file('ids.txt')
    groups = open_file('groups.txt')
    if str(message.chat.id) not in ids and str(message.text).lower() in groups:
        markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
        file_user_id(message.chat.id, groups[message.text.lower()])
        file = open('users.txt', 'a')
        file.write(str(message.from_user.username) + '\n')
        file.close()
        bot.send_message(440453234,'@' + message.from_user.username + ' ' + 'just registred!')
        print(message.from_user.username, 'just registred!')
        bot.send_message(message.chat.id, f'Регистрация успешно завершена!\n<b>Ваша группа: {message.text}</b>\n<i>Поменять группу можно в меню настроек</i>', reply_markup=markup_reply,  parse_mode='HTML')
        keyboard = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text="На сегодня", callback_data="today")
        callback_button_2 = types.InlineKeyboardButton(text="На завтра", callback_data="tomorrow")
        callback_button_3 = types.InlineKeyboardButton(text="На эту неделю", callback_data="week")
        callback_button_4 = types.InlineKeyboardButton(text="На следующую неделю", callback_data="nxtweek")
        keyboard.add(callback_button, callback_button_2, callback_button_3, callback_button_4)
        bot.send_message(message.chat.id, "На какой день прислать расписание?", reply_markup=keyboard)
    elif str(message.chat.id) in ids:
        msg = bot.send_message(message.chat.id, 'Вы уже зарегистрированы')
        bot.register_next_step_handler(msg, begin)
    else:
        msg = bot.send_message(message.chat.id, 'Я не знаю такую группу.\n<i>Пожалуйста, проверьте номер группы.</i>', parse_mode='HTML')
        bot.register_next_step_handler(msg, register)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    ids = open_file('ids.txt')
    if call.message:
        if call.data == "today":
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text="На сегодня", callback_data="today")
            callback_button_2 = types.InlineKeyboardButton(text="На завтра", callback_data="tomorrow")
            callback_button_3 = types.InlineKeyboardButton(text="На эту неделю", callback_data="week")
            callback_button_4 = types.InlineKeyboardButton(text="На следующую неделю", callback_data="nxtweek")
            keyboard.add(callback_button, callback_button_2, callback_button_3, callback_button_4)
            today = datetime.date.today()
            if today.isoweekday() == 7:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Сегодня воскресенье!", reply_markup=keyboard)
            else:
                if str(call.message.chat.id) in ids:
                    today = datetime.date.today()
                    res = parse_day(get_url(call.message.chat.id, today), today)
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=res,
                                          parse_mode='HTML', reply_markup=keyboard)
                else:
                    msg = bot.send_message(call.message.chat.id, 'Я не знаю, какая у вас группа.\nПожалуйста, пришлите мне номер группы.', parse_mode='HTML')
                    bot.register_next_step_handler(msg, register)
        if call.data == "tomorrow":
            today = datetime.date.today()
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text="На сегодня", callback_data="today")
            callback_button_2 = types.InlineKeyboardButton(text="На завтра", callback_data="tomorrow")
            callback_button_3 = types.InlineKeyboardButton(text="На эту неделю", callback_data="week")
            callback_button_4 = types.InlineKeyboardButton(text="На следующую неделю", callback_data="nxtweek")
            keyboard.add(callback_button, callback_button_2, callback_button_3, callback_button_4)
            if today.isoweekday() == 6:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text="Завтра воскресенье!", reply_markup=keyboard)
            elif today.isoweekday() == 7:
                if str(call.message.chat.id) in ids:
                    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
                    res = parse_day(get_url(call.message.chat.id, tomorrow), tomorrow)
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=res,
                                          parse_mode='HTML', reply_markup=keyboard)
            else:
                if str(call.message.chat.id) in ids:
                    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
                    res = parse_day(get_url(call.message.chat.id, today), tomorrow)
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=res, parse_mode='HTML', reply_markup=keyboard)
                else:
                    msg = bot.send_message(call.message.chat.id, 'Я не знаю, какая у вас группа.\nПожалуйста, пришлите мне номер группы.', parse_mode='HTML')
                    bot.register_next_step_handler(msg, register)
        if call.data == 'week':
            today = datetime.date.today()
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text="На сегодня", callback_data="today")
            callback_button_2 = types.InlineKeyboardButton(text="На завтра", callback_data="tomorrow")
            callback_button_3 = types.InlineKeyboardButton(text="На эту неделю", callback_data="week")
            callback_button_4 = types.InlineKeyboardButton(text="На следующую неделю", callback_data="nxtweek")
            keyboard.add(callback_button, callback_button_2, callback_button_3, callback_button_4)
            if str(call.message.chat.id) in ids:
                today = datetime.date.today()
                t = parse(get_url(call.message.chat.id, today))
                res =''
                for i in t:
                    res += '\n'.join(i)
                    if i != t[-1] and i != t[-2]:
                        res += '\n\n\n' #+ ' ' * 39 + '\n'
                if res:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=res, parse_mode='HTML', reply_markup=keyboard)
                else:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="<i>На этой неделе занятий нет.</i>",
                                          parse_mode='HTML', reply_markup=keyboard)
            else:
                msg = bot.send_message(call.message.chat.id, 'Я не знаю, какая у вас группа.\nПожалуйста, пришлите мне номер группы.', parse_mode='HTML')
                bot.register_next_step_handler(msg, register)
        if call.data == 'nxtweek':
            today = datetime.date.today()
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text="На сегодня", callback_data="today")
            callback_button_2 = types.InlineKeyboardButton(text="На завтра", callback_data="tomorrow")
            callback_button_3 = types.InlineKeyboardButton(text="На эту неделю", callback_data="week")
            callback_button_4 = types.InlineKeyboardButton(text="На следующую неделю", callback_data="nxtweek")
            keyboard.add(callback_button, callback_button_2, callback_button_3, callback_button_4)
            if str(call.message.chat.id) in ids:
                #if today.isoweekday() == 7:
                    #nxt = today + datetime.timedelta(days=7)
                    #nxt_url = get_url(call.message.chat.id, nxt)
                #else:
                nxt = today + datetime.timedelta(days=7)
                nxt_url = get_url(call.message.chat.id, nxt)
                nxt_week = parse(nxt_url)
                res = ''
                for i in nxt_week:
                    res += '\n'.join(i)
                    if i != nxt_week[-1] and i != nxt_week[-2]:
                        res += '\n\n\n'  # + ' ' * 39 + '\n'
                if res:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=res,
                                          parse_mode='HTML', reply_markup=keyboard)
                else:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text="<i>На следующей неделе занятий нет.</i>",
                                          parse_mode='HTML', reply_markup=keyboard)
            else:
                msg = bot.send_message(call.message.chat.id, 'Я не знаю, какая у вас группа.\nПожалуйста, пришлите мне номер группы.', parse_mode='HTML')
                bot.register_next_step_handler(msg, register)
        if call.data == 'edit_group':
            ids = open_file('ids.txt')
            if str(call.message.chat.id) in ids:
                ids.pop(str(call.message.chat.id))
                msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=
                '<i>Введите новый номер группы</i>', parse_mode='HTML')
                bot.register_next_step_handler(msg, register)
                file = open('ids.txt', 'w')
                for key, value in ids.items():
                    file.write(f'{key};{value}\n')
                file.close()
            else:
                msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=
                                       'Группа уже сброшена, <i>пришлите мне новый номер вашей группы</i>', parse_mode='HTML')
                bot.register_next_step_handler(msg, register)
        if call.data == 'contact':
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text="Назад", callback_data="back")
            keyboard.add(callback_button)
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Авторы проекта:\n@nolifeleftt\n@plutoshka\nПо всем вопросам, предложениям и замечаниям вы можете обращаться к нам в лс, или же вы можете написать сообщение боту, находясь в этом меню.\n<b>Убедительная просьба описывать проблему одним сообщением.</b>\n<i>Мы обязательно Вам поможем</i>❤\n\nЕсли вы хотите поддержать проект, помочь с оплатой хостинга или просто поблагодарить создателей:\n<b>2202 2022 4665 7088</b>",
                                  parse_mode='HTML', reply_markup=keyboard)
            bot.register_next_step_handler(msg, cont)
        if call.data == 'back':
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text="Сменить группу", callback_data="edit_group")
            callback_button_2 = types.InlineKeyboardButton(text="Связаться с нами", callback_data="contact")
            keyboard.add(callback_button, callback_button_2)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Вы находитесь в меню настроек", reply_markup=keyboard)
def cont(message):
    if message.text:
        bot.send_message(440453234, message.from_user.username + ' сообщает:\n' + message.text)

@bot.message_handler(commands=['rasp'])
def rasp(message):
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="На сегодня", callback_data="today")
    callback_button_2 = types.InlineKeyboardButton(text="На завтра", callback_data="tomorrow")
    callback_button_3 = types.InlineKeyboardButton(text="На эту неделю", callback_data="week")
    callback_button_4 = types.InlineKeyboardButton(text="На следующую неделю", callback_data="nxtweek")
    keyboard.add(callback_button, callback_button_2, callback_button_3, callback_button_4)
    bot.send_message(message.chat.id, "На какой день прислать расписание?", reply_markup=keyboard)
@bot.message_handler(commands=['settings'])
def sets(message):
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Сменить группу", callback_data="edit_group")
    callback_button_2 = types.InlineKeyboardButton(text="Связаться с нами", callback_data="contact")
    callback_button_3 = types.InlineKeyboardButton(text="Назад", callback_data="today")
    keyboard.add(callback_button, callback_button_2, callback_button_3)
    bot.send_message(message.chat.id, "Вы находитесь в меню настроек." , reply_markup=keyboard)
bot.infinity_polling(timeout=10, long_polling_timeout=5)