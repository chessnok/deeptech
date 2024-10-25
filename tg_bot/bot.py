import telebot
from dotenv import dotenv_values
import requests
from engine import get_conn
from models import User
from sqlalchemy import select
import uuid


bot = telebot.TeleBot(dotenv_values('.env')['TOKEN'])
conn = get_conn()


def apply_to_model(message: telebot.types.Message, conversation_id: uuid) -> str:
    url = dotenv_values('.env')['MODEL_URL']
    response = requests.post(url, json={'text': message.text, 
                                        'user_id': message.from_user.id, 
                                        'conversation_id': conversation_id})
    text = response.json()['text']
    return text


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello, {0.first_name}!".format(message.from_user))
    

@bot.message_handler(commands=['new'])
def change_conversation_id(message):
    s = select([User]).where(~(User.id == message.from_user.id))
    user = conn.execute(s).first()
    if user is None:
        conversation_id = uuid.uuid4()
        conn.execute(
            User.insert().values(
                id=message.from_user.id, 
                first_name=message.from_user.first_name,
                conversation_id=conversation_id
            )
        )
    else:
        conn.execute(
            User.update().where(User.id == message.from_user.id).values(
                conversation_id=uuid.uuid4()
            )
        )
    bot.reply_to(message, "Контекст чата очищен")
    
    
@bot.message_handler(commands=['test'])
def test(message):
    user = conn.execute(select([User]).where(User.id == message.from_user.id)).first()
    if user is None:
        bot.reply_to(message, "Ты не зарегистрирован")
        conversation_id = uuid.uuid4()
        conn.execute(
            User.insert().values(
                id=message.from_user.id,
                first_name=message.from_user.first_name,
                conversation_id=conversation_id
            )
        )
    else:
        bot.reply_to(message, f"Ты зарегистрирован, Твое имя {user.first_name}, Твой ID {user.id}, "
                              f"Твой контекст {user.conversation_id}")


@bot.message_handler()
def process_message(message):
    s = select([User]).where(~(User.id == message.from_user.id))
    user = conn.execute(s).first()
    if user is None:
        conversation_id = uuid.uuid4()
        conn.execute(
            User.insert().values(
                id=message.from_user.id, 
                first_name=message.from_user.first_name,
                conversation_id=conversation_id
            )
        )
    else:
        conversation_id = user.conversation_id
    apply_to_model(message, conversation_id)
    bot.reply_to(message, "Я тупой бот, скоро тут будет ответ ML")
