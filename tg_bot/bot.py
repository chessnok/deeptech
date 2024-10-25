import telebot
from dotenv import dotenv_values
from engine import get_conn
from models import User
import uuid
from sqlalchemy import select, exists
import requests

bot = telebot.TeleBot(dotenv_values('.env')['TOKEN'])
conn = get_conn()


def apply_to_model(message: telebot.types.Message,
                   conversation_id: uuid) -> str:
    url = dotenv_values('.env')['MODEL_URL']
    response = requests.post(f"{url}/new_message", json={"text": message.text,
                                                         'conversation_id': conversation_id})
    text = response.json()['text']
    return text


def new_conversation(user_id: int):
    connection = get_conn()
    url = f"{dotenv_values('.env')['BACKEND_URL']}/new_conversation"
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
        stmt).fetchone()  # Выполняем запрос и получаем первую строку

    if result:
        return result[0]
    else:
        return None  # Возвращаем None, если запись не найдена


@bot.message_handler(commands=['start'])
def send_welcome(message):
    new_conversation(message.from_user.id)
    bot.reply_to(message, "Привет, {0.first_name}!".format(message.from_user))


@bot.message_handler(commands=['new'])
def change_conversation_id(message):
    new_conversation(message.from_user.id)
    bot.reply_to(message, "Контекст чата очищен")


@bot.message_handler()
def process_message(message):
    # apply_to_model(message, conversation_id) // TODO: Когда будет работать ML
    bot.reply_to(message,
                 f"Я тупой бот, скоро тут будет ответ ML, Текущий контекст: {get_conversation_id(message.from_user.id)}")
