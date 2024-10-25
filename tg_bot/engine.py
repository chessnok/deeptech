from dotenv import dotenv_values
from sqlalchemy import create_engine

engine = create_engine(dotenv_values(".env")["DB_URL"])


def get_engine():
    return engine


def get_conn():
    return engine.connect()
