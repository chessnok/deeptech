import logging

from decouple import config
import telebot
from telebot.types import BotCommand, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message

from engine import get_conn
from models import User, Message_author_map
import uuid
from sqlalchemy import select, exists
import requests

bot = telebot.TeleBot(config('TOKEN', default=''))
conn = get_conn()
apikey = config('APIKEY', default='')
admin_group_id = config('ADMIN_GROUP_ID', default='')


def send_files(chat_id, files):
    for file_path in files:
        with open(file_path, 'rb') as file:
            bot.send_document(chat_id, file)


def apply_to_model(message: telebot.types.Message,
                   conversation_id: uuid) -> (str, int):
    url = config('BACKEND_URL')
    response = requests.post(f"{url}/new_message", json={"text": message.text,
                                                         'conversation_id': str(
                                                             conversation_id)})
    response.raise_for_status()
    text = response.json()['text']
    code = response.json()['images']
    return text, code


def new_conversation(user_id: int):
    url = f"{config('BACKEND_URL')}/new_conv"
    response = requests.post(url)
    response.raise_for_status()
    conversation_id = response.json()['uuid']
    stmt = select(exists().where(User.c.tg_id == user_id))
    if user_exists := conn.execute(stmt).scalar():
        conn.execute(
            User.update()
            .where(User.c.tg_id == user_id)
            .values(conversation_id=conversation_id)
        )

    else:
        conn.execute(
            User.insert().values(tg_id=user_id,
                                 conversation_id=conversation_id)
        )
    conn.commit()


def get_conversation_id(user_id: int):
    stmt = select(User.c.conversation_id).where(User.c.tg_id == user_id)
    return result[0] if (result := conn.execute(stmt).fetchone()) else None

def get_user_id(message_id: int):
    stmt = select(Message_author_map.c.author_id).where(Message_author_map.c.message_id == message_id)
    return result[0] if (result := conn.execute(stmt).fetchone()) else None

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


@bot.message_handler(func=lambda message: message.chat.type == 'private')
def process_message(message: Message):
    conv = get_conversation_id(message.from_user.id)
    text,images = apply_to_model(message, conv)
    if 'нет ответа' in text.lower():
        text = "Админ"
        code = 3
    else:
        code = 1
    if code == 1:
        im = ['Aspose.Words.c13446d9-bf31-4bd4-a80f-8f3f393359ee.002.png', 'Aspose.Words.c13446d9-bf31-4bd4-a80f-8f3f393359ee.011.png']
        im = [f"images/{i}" for i in im]
        bot.reply_to(message, text)
        send_files(message.chat.id, im)
    else:
        markup = InlineKeyboardMarkup()
        button = InlineKeyboardButton("Отправить вопрос администраторам", callback_data="send_to_admins")
        markup.add(button)
        conn.commit()
        bot.reply_to(message, "Мы не смогли найти ответ на ваш вопрос. "
                              "Однако вы можете обратиться за помощью к администратору.", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "send_to_admins")
def handle_callback(call: CallbackQuery):
    user = call.from_user
    question_text = f"Вопрос от {user.first_name} {user.last_name or ''} (@{user.username or 'нет юзернейма'}): {call.message.reply_to_message.text}"
    msg = bot.send_message(admin_group_id, question_text)
    if msg:
        conn.execute(
            Message_author_map.insert().values(message_id=msg.message_id,
                                               author_id=user.id)
        )
        bot.answer_callback_query(call.id, "Ваш вопрос отправлен администраторам.")
        bot.send_message(call.message.chat.id, "Ваш вопрос был отправлен администраторам. Ожидайте ответа.")
    else:
        bot.send_message(call.message.chat.id, "Ошибка при отправке вопроса.")


@bot.message_handler(func=lambda message: message.chat.id == int(admin_group_id))
def check_reply_message(message: Message) -> None:
    """
    Проверяет, является ли сообщение ответом, и если да, отправляет текст ответа нужному пользователю.
    """
    if message.reply_to_message:
        original_message_id = message.reply_to_message
        author_id = get_user_id(original_message_id.message_id)
        if author_id:
            bot.send_message(
                chat_id=author_id,
                text=f"Ответ администраторов:\n{message.text}"
            )
        else:
            logging.info("Автор сообщения не найден в базе данных.")
