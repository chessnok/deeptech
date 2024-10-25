import telebot
from dotenv import dotenv_values


bot = telebot.TeleBot(dotenv_values('.env')['TOKEN'])


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello, {0.first_name}!".format(message.from_user))


@bot.message_handler()
def echo_all(message):
    bot.reply_to(message, "Я тупой бот, скоро тут будет ответ ML")