import dotenv
from bot import bot
import logging

logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    dotenv.load_dotenv()    # load .env
    logging.info('Starting bot...')
    bot.polling(none_stop=True)



