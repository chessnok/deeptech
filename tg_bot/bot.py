from decouple import config
import telebot
from telebot.types import BotCommand

from engine import get_conn
from models import User
import uuid
from sqlalchemy import select, exists
import requests

bot = telebot.TeleBot(config('TOKEN', default=''))
conn = get_conn()
apikey = config('APIKEY', default='')


def apply_to_model(message: telebot.types.Message,
                   conversation_id: uuid) -> str:
    url = config('BACKEND_URL')
    response = requests.post(f"{url}/new_message", json={"text": message.text,
                                                         'conversation_id': str(
                                                             conversation_id)})
    response.raise_for_status()
    text = response.json()['text']
    return text


def new_conversation(user_id: int):
    connection = get_conn()
    url = f"{config('BACKEND_URL')}/new_conv"
    response = requests.post(url)
    response.raise_for_status()
    conversation_id = response.json()['uuid']
    stmt = select(exists().where(User.c.tg_id == user_id))
    user_exists = connection.execute(
        stmt).scalar()

    if not user_exists:
        connection.execute(
            User.insert().values(tg_id=user_id,
                                 conversation_id=conversation_id)
        )
    else:
        connection.execute(
            User.update()
            .where(User.c.tg_id == user_id)
            .values(conversation_id=conversation_id)
        )

    connection.commit()


def get_conversation_id(user_id: int):
    connection = get_conn()  # Получаем соединение
    stmt = select(User.c.conversation_id).where(User.c.tg_id == user_id)
    result = connection.execute(
        stmt).fetchone()

    if result:
        return result[0]
    else:
        return None  # Возвращаем None, если запись не найдена


@bot.message_handler(commands=['start'])
def send_welcome(message):
    new_conversation(message.from_user.id)
    bot.reply_to(message, f"Привет, {message.from_user.first_name}! Это бот технической документации. Что бы задать свой вопрос о документации просто напиши его, а что бы начать новую переписку /new")
    bot.set_my_commands([
        BotCommand("/new", "Начать новую переписку!")
    ])

@bot.message_handler(commands=['new'])
def change_conversation_id(message):
    new_conversation(message.from_user.id)
    bot.reply_to(message, "Надеюсь я ответил на твой предыдущий вопрос. Начнем новую переписку. Просто напиши свой вопрос о документации")


@bot.message_handler()
def process_message(message):
    conv = get_conversation_id(message.from_user.id)
    res = apply_to_model(message, conv)
    bot.reply_to(message, res)
