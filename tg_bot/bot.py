import telebot
from dotenv import dotenv_values
import requests


bot = telebot.TeleBot(dotenv_values('.env')['TOKEN'])


def apply_to_model(message) -> str:
    url = dotenv_values('.env')['MODEL_URL']
    response = requests.post(url, json={'text': message.text})
    text = response.json()['text']
    return text


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello, {0.first_name}!".format(message.from_user))


@bot.message_handler()
def echo_all(message):
    bot.reply_to(message, "Я тупой бот, скоро тут будет ответ ML")