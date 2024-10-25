from dotenv import dotenv_values
from sqlalchemy import create_engine

password = dotenv_values('.env')['DB_PASSWORD']
user = dotenv_values('.env')['DB_USER']
host = dotenv_values('.env')['DB_HOST']
db = dotenv_values('.env')['DB_NAME']

engine = create_engine(f'postgresql://{user}:{password}@{host}/{db}')


def get_engine():
    return engine


def get_conn():
    return engine.connect()
