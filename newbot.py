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

bot = telebot.TeleBot('5741562885:AAE0B_c2HMWYTNS0HA_c1HnkJE4ttq7vTD4')
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

@bot.message_handler(commands=['start'])
def begin(message):
    ids = open_file('ids.txt')
    if str(message.chat.id) not in ids:
        markup_reply = types.InlineKeyboardMarkup()
        btn_my_site = types.InlineKeyboardButton(text='Расписание', url='https://ruz.spbstu.ru')
        markup_reply.add(btn_my_site)
        msg = bot.send_message(message.chat.id,
                                  'Привет! Чтобы начать получать расписание, нужно передать ссылку на расписание своей группы.\n\n<i>Найти ее можно нажав на кнопку ниже или перейдя сюда</i>: https://ruz.spbstu.ru/ и указав свои институт, курс и группу.',
                                  reply_markup=markup_reply, parse_mode='HTML')
        bot.register_next_step_handler(msg, register)
        bot.send_message(message.chat.id, 'После того, как скоприруешь ссылку отправь ее мне.', parse_mode='HTML')

    else:
        keyboard = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text="На сегодня", callback_data="today")
        callback_button_2 = types.InlineKeyboardButton(text="На завтра", callback_data="tomorrow")
        callback_button_3 = types.InlineKeyboardButton(text="На эту неделю", callback_data="week")
        callback_button_4 = types.InlineKeyboardButton(text="На следующую неделю", callback_data="nxtweek")
        callback_button_5 = types.InlineKeyboardButton(text="Настройки", callback_data="settings")
        keyboard.add(callback_button, callback_button_2, callback_button_3, callback_button_4, callback_button_5)
        bot.send_message(message.chat.id, "На какой день прислать расписание?", reply_markup=keyboard)
def register(message):
    ids = open_file('ids.txt')
    if 'ruz' in str(message.text).strip() and str(message.chat.id) not in ids:
        if check_link(message.text.split()[-1]):
            markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
            file_user_id(message.chat.id, message.text.split()[-1])
            file = open('users.txt', 'a')
            file.write(str(message.from_user.username) + '\n')
            file.close()
            bot.send_message(440453234, message.from_user.username + ' ' + 'just registred!')
            print(message.from_user.username, 'just registred!')
            bot.send_message(message.chat.id, '<i>Регистрация успешно завершена!</i>\n\n<i>Если вы указали не ту ссылку или хотите сменить группу, нажмите "Настройки" -> "Сброс" и укажите новую ссылку.</i>', reply_markup=markup_reply,  parse_mode='HTML')
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text="На сегодня", callback_data="today")
            callback_button_2 = types.InlineKeyboardButton(text="На завтра", callback_data="tomorrow")
            callback_button_3 = types.InlineKeyboardButton(text="На эту неделю", callback_data="week")
            callback_button_4 = types.InlineKeyboardButton(text="На следующую неделю", callback_data="nxtweek")
            callback_button_5 = types.InlineKeyboardButton(text="Настройки", callback_data="settings")
            keyboard.add(callback_button, callback_button_2, callback_button_3, callback_button_4, callback_button_5)
            bot.send_message(message.chat.id, "На какой день прислать расписание?", reply_markup=keyboard)
        else:
            markup_reply = types.InlineKeyboardMarkup()
            btn_my_site = types.InlineKeyboardButton(text='Расписание', url='https://ruz.spbstu.ru')
            markup_reply.add(btn_my_site)
            msg = bot.send_message(message.chat.id, 'Неверная ссылка. Укажите правильную ссылку на расписание вашей группы', reply_markup=markup_reply)
            bot.register_next_step_handler(msg, register)
@bot.message_handler(content_types=["text"])
def any_msg(message):
    if message.text == 'Получить расписание':
        keyboard = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text="На сегодня", callback_data="today")
        callback_button_2 = types.InlineKeyboardButton(text="На завтра", callback_data="tomorrow")
        callback_button_3 = types.InlineKeyboardButton(text="На эту неделю", callback_data="week")
        callback_button_4 = types.InlineKeyboardButton(text="На следующую неделю", callback_data="nxtweek")
        callback_button_5 = types.InlineKeyboardButton(text="Настройки", callback_data="settings")
        keyboard.add(callback_button, callback_button_2, callback_button_3, callback_button_4, callback_button_5)
        bot.send_message(message.chat.id, "На какой день прислать расписание?", reply_markup=keyboard)
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    ids = open_file('ids.txt')
    # Если сообщение из чата с ботом
    if call.message:
        if call.data == "today":
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text="На сегодня", callback_data="today")
            callback_button_2 = types.InlineKeyboardButton(text="На завтра", callback_data="tomorrow")
            callback_button_3 = types.InlineKeyboardButton(text="На эту неделю", callback_data="week")
            callback_button_4 = types.InlineKeyboardButton(text="На следующую неделю", callback_data="nxtweek")
            callback_button_5 = types.InlineKeyboardButton(text="Настройки", callback_data="settings")
            keyboard.add(callback_button, callback_button_2, callback_button_3, callback_button_4, callback_button_5)
            today = datetime.date.today()
            if today.isoweekday() == 7:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Сегодня воскресенье!", reply_markup=keyboard)
            else:
                if str(call.message.chat.id) in ids:
                    t = parse(get_url(call.message.chat.id, today))
                    res = '\n'.join(t[today.weekday()])
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text=res, reply_markup=keyboard, parse_mode='HTML')
                else:
                    markup_reply = types.InlineKeyboardMarkup()
                    btn_my_site = types.InlineKeyboardButton(text='Сайт с расписанием', url='https://ruz.spbstu.ru')
                    markup_reply.add(btn_my_site)
                    msg = bot.send_message(call.message.chat.id, 'У меня нет ссылки на ваше расписание.\nПожалуйста, пришлите мне ссылку на ваше расписание.', reply_markup=markup_reply, parse_mode='HTML')
                    bot.register_next_step_handler(msg, register)
        if call.data == "tomorrow":
            today = datetime.date.today()
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text="На сегодня", callback_data="today")
            callback_button_2 = types.InlineKeyboardButton(text="На завтра", callback_data="tomorrow")
            callback_button_3 = types.InlineKeyboardButton(text="На эту неделю", callback_data="week")
            callback_button_4 = types.InlineKeyboardButton(text="На следующую неделю", callback_data="nxtweek")
            callback_button_5 = types.InlineKeyboardButton(text="Настройки", callback_data="settings")
            keyboard.add(callback_button, callback_button_2, callback_button_3, callback_button_4, callback_button_5)
            if today.isoweekday() == 6:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text="Сегодня воскресенье!", reply_markup=keyboard)
            elif today.isoweekday() == 7:
                t = parse(get_url(call.message.chat.id, today + datetime.timedelta(days=1)))
                res = ' ' * 39 + '\n'.join(t[0]) + '\n' + ' ' * 39
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=res, parse_mode='HTML', reply_markup=keyboard)
            else:
                if str(call.message.chat.id) in ids:
                    t = parse(get_url(call.message.chat.id, today))
                    res = ' ' * 39 + '\n'.join(t[today.weekday() + 1]) + '\n' + ' ' * 39
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=res, parse_mode='HTML', reply_markup=keyboard)
                else:
                    markup_reply = types.InlineKeyboardMarkup()
                    btn_my_site = types.InlineKeyboardButton(text='Сайт с расписанием', url='https://ruz.spbstu.ru')
                    markup_reply.add(btn_my_site)
                    msg = bot.send_message(call.message.chat.id, 'У меня нет ссылки на ваше расписание.\nПожалуйста, пришлите мне ссылку на ваше расписание.', reply_markup=markup_reply, parse_mode='HTML')
                    bot.register_next_step_handler(msg, register)
        if call.data == 'week':
            today = datetime.date.today()
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text="На сегодня", callback_data="today")
            callback_button_2 = types.InlineKeyboardButton(text="На завтра", callback_data="tomorrow")
            callback_button_3 = types.InlineKeyboardButton(text="На эту неделю", callback_data="week")
            callback_button_4 = types.InlineKeyboardButton(text="На следующую неделю", callback_data="nxtweek")
            callback_button_5 = types.InlineKeyboardButton(text="Настройки", callback_data="settings")
            keyboard.add(callback_button, callback_button_2, callback_button_3, callback_button_4, callback_button_5)
            if str(call.message.chat.id) in ids:
                today = datetime.date.today()
                t = parse(get_url(call.message.chat.id, today))
                res =''
                for i in t:
                    res += '\n'.join(i)
                    if i != t[-1] and i != t[-2]:
                        res += '\n\n\n' #+ ' ' * 39 + '\n'
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=res, parse_mode='HTML', reply_markup=keyboard)
            else:
                markup_reply = types.InlineKeyboardMarkup()
                btn_my_site = types.InlineKeyboardButton(text='Сайт с расписанием', url='https://ruz.spbstu.ru')
                markup_reply.add(btn_my_site)
                msg = bot.send_message(call.message.chat.id, 'У меня нет ссылки на ваше расписание.\nПожалуйста, пришлите мне ссылку на ваше расписание.', reply_markup=markup_reply, parse_mode='HTML')
                bot.register_next_step_handler(msg, register)
        if call.data == 'nxtweek':
            today = datetime.date.today()
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text="На сегодня", callback_data="today")
            callback_button_2 = types.InlineKeyboardButton(text="На завтра", callback_data="tomorrow")
            callback_button_3 = types.InlineKeyboardButton(text="На эту неделю", callback_data="week")
            callback_button_4 = types.InlineKeyboardButton(text="На следующую неделю", callback_data="nxtweek")
            callback_button_5 = types.InlineKeyboardButton(text="Настройки", callback_data="settings")
            keyboard.add(callback_button, callback_button_2, callback_button_3, callback_button_4, callback_button_5)
            if str(call.message.chat.id) in ids:
                if today.isoweekday() == 7:
                    nxt = today + datetime.timedelta(days=8)
                    nxt_url = get_url(call.message.chat.id, nxt)
                else:
                    nxt = today + datetime.timedelta(days=7)
                    nxt_url = get_url(call.message.chat.id, nxt)
                nxt_week = parse(nxt_url)
                res = ''
                for i in nxt_week:
                    res += '\n'.join(i)
                    if i != nxt_week[-1] and i != nxt_week[-2]:
                        res += '\n\n\n'  # + ' ' * 39 + '\n'
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=res, parse_mode='HTML', reply_markup=keyboard)
            else:
                markup_reply = types.InlineKeyboardMarkup()
                btn_my_site = types.InlineKeyboardButton(text='Сайт с расписанием', url='https://ruz.spbstu.ru')
                markup_reply.add(btn_my_site)
                msg = bot.send_message(call.message.chat.id, 'У меня нет ссылки на ваше расписание.\nПожалуйста, пришлите мне ссылку на ваше расписание.', reply_markup=markup_reply, parse_mode='HTML')
                bot.register_next_step_handler(msg, register)
        if call.data == 'contact':
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text="Назад", callback_data="back")
            keyboard.add(callback_button)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Авторы проекта:\n@nolifeleftt\n@plutoshka\nПо всем вопросам, предложениям и замечаниям вы можете обращаться к нам, мы обязательно Вам поможем❤", parse_mode='HTML', reply_markup=keyboard)
        if call.data == 'clear_link':
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text="Да", callback_data="yesclear")
            callback_button_2 = types.InlineKeyboardButton(text="Нет", callback_data="noclear")
            keyboard.add(callback_button, callback_button_2)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Ваша ссылка будет сброшена, вы уверены?', reply_markup=keyboard)
        if call.data == 'yesclear':
            ids = open_file('ids.txt')
            if str(call.message.chat.id) in ids:
                ids.pop(str(call.message.chat.id))
                markup_reply = types.InlineKeyboardMarkup()
                btn_my_site = types.InlineKeyboardButton(text='Сайт с расписанием', url='https://ruz.spbstu.ru')
                markup_reply.add(btn_my_site)
                msg = bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id, text =
                                          'Ссылка сброшена, <i>пришлите мне новую ссылку на расписание вашей группы</i>', parse_mode='HTML')
                bot.register_next_step_handler(msg, register)
                file = open('ids.txt', 'w')
                for key, value in ids.items():
                    file.write(f'{key};{value}\n')
                file.close()
            else:
                markup_reply = types.InlineKeyboardMarkup()
                btn_my_site = types.InlineKeyboardButton(text='Сайт с расписанием', url='https://ruz.spbstu.ru')
                markup_reply.add(btn_my_site)
                msg = bot.send_message(call.message.chat.id,
                                          'Ссылка уже сброшена, <i>пришлите мне новую ссылку на расписание вашей группы</i>',
                                          reply_markup=markup_reply, parse_mode='HTML')
                bot.register_next_step_handler(msg, register)
        if call.data == 'noclear':
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text="Связаться с нами", callback_data="contact")
            callback_button_2 = types.InlineKeyboardButton(text="Сбросить ссылку", callback_data="clear_link")
            callback_button_3 = types.InlineKeyboardButton(text="Назад", callback_data="back")
            keyboard.add(callback_button, callback_button_2, callback_button_3)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=
            "<b>Вы находитесь в меню настроек</b>", reply_markup=keyboard, parse_mode='HTML')
        if call.data == 'settings':
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text="Связаться с нами", callback_data="contact")
            callback_button_2 = types.InlineKeyboardButton(text="Сброс", callback_data="clear_link")
            callback_button_3 = types.InlineKeyboardButton(text="Назад", callback_data="back")
            keyboard.add(callback_button, callback_button_2, callback_button_3)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=
            "<b>Вы находитесь в меню настроек</b>", reply_markup=keyboard, parse_mode='HTML')
        if call.data == 'back':
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text="На сегодня", callback_data="today")
            callback_button_2 = types.InlineKeyboardButton(text="На завтра", callback_data="tomorrow")
            callback_button_3 = types.InlineKeyboardButton(text="На эту неделю", callback_data="week")
            callback_button_4 = types.InlineKeyboardButton(text="На следующую неделю", callback_data="nxtweek")
            callback_button_5 = types.InlineKeyboardButton(text="Настройки", callback_data="settings")
            keyboard.add(callback_button, callback_button_2, callback_button_3, callback_button_4, callback_button_5)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=
            "На какой день прислать расписание?", reply_markup=keyboard, parse_mode='HTML')

bot.infinity_polling(timeout=10, long_polling_timeout=5)