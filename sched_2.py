import telebot
import sqlite3
from telebot import types
class User:
    def __init__(self, username, id, name):
        self.username = username
        self.id = id
        self.name = name
    def getInfo(self):
        return [self.username, self.id, self.name]

conn = sqlite3.connect('users.db')
bot = telebot.TeleBot('5682201668:AAFUU_Cv5p1feZzn4g5l1JFuJDh7FHdrNwM')
@bot.message_handler(commands=['start'])
def init(message):
    user = User(message.from_user.username, str(message.chat.id), 'test')
    bot.send_message(message.chat.id, ' '.join(user.getInfo()))
    print(user.getInfo())
# print(user.getInfo()[0])
bot.infinity_polling(timeout=10, long_polling_timeout=5)