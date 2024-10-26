from decouple import config
import telebot
from telebot import types
from telebot.types import BotCommand, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message

from engine import get_conn
from models import User
import uuid
from sqlalchemy import select, exists
import requests

bot = telebot.TeleBot(config('TOKEN', default=''))
conn = get_conn()
apikey = config('APIKEY', default='')
admin_group_id = config('ADMIN_GROUP_ID', default='')

message_map = {}


def apply_to_model(message: telebot.types.Message,
                   conversation_id: uuid) -> (str, int):
    url = config('BACKEND_URL')
    response = requests.post(f"{url}/new_message", json={"text": message.text,
                                                         'conversation_id': str(
                                                             conversation_id)})
    response.raise_for_status()
    text = response.json()['text']
    code = response.json()['code']
    return text, code


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


@bot.message_handler(commands=['start'], func=lambda message: message.chat.type == 'private')
def send_welcome(message):
    new_conversation(message.from_user.id)
    bot.reply_to(message, f"Привет, {message.from_user.first_name}! Это бот технической документации. Что бы задать свой вопрос о документации просто напиши его, а что бы начать новую переписку /new")
    bot.set_my_commands([
        BotCommand("/new", "Начать новую переписку!")
    ])


@bot.message_handler(commands=['new'], func=lambda message: message.chat.type == 'private')
def change_conversation_id(message):
    new_conversation(message.from_user.id)
    bot.reply_to(message, "Надеюсь я ответил на твой предыдущий вопрос) Очищаю контекст переписки. Просто напиши "
                          "свой новый вопрос о документации")


def send_question_to_admin(message):
    bot.send_message(admin_group_id, message)


@bot.message_handler(func=lambda message: message.chat.type == 'private')
def process_message(message):
    conv = get_conversation_id(message.from_user.id)
    text, code = apply_to_model(message, conv)
    if code == 1:
        bot.reply_to(message, text)
    elif code == 2:
        bot.reply_to(message, "К сожалению ответа на ваш вопрос нет в документации. \n" + text)
    else:
        markup = InlineKeyboardMarkup()
        button = InlineKeyboardButton("Отправить вопрос администраторам", callback_data="send_to_admins")
        markup.add(button)
        message_map[message.message_id] = message.from_user.id
        bot.reply_to(message, "Мы не смогли найти ответ на ваш вопрос. "
                              "Однако вы можете обратиться за помощью к администратору. @", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "send_to_admins")
def handle_callback(call: CallbackQuery):
    user = call.from_user
    question_text = f"Вопрос от {user.first_name} {user.last_name or ''} (@{user.username or 'нет юзернейма'}):"
    bot.send_message(admin_group_id, question_text)
    bot.forward_message(admin_group_id, call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, "Ваш вопрос отправлен администраторам.")
    bot.send_message(call.message.chat.id, "Ваш вопрос был отправлен администраторам. Ожидайте ответа.")


@bot.message_handler(func=lambda message: message.chat.type == 'group')
def check_reply_message(message: Message) -> None:
    """
    Проверяет, является ли сообщение ответом, и если да, выводит ID исходного сообщения.
    """
    if message.reply_to_message:
        original_message_id = message.reply_to_message.message_id
        author_id = message_map[original_message_id]
        bot.send_message(
            chat_id=author_id,
            text=f"Ответ администраторов: \n {message.text}"
        )
