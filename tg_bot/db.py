from sqlalchemy import create_engine
from dotenv import dotenv_values


def get_engine():
    password = dotenv_values('.env')['DB_PASSWORD']
    user = dotenv_values('.env')['DB_USER']
    host = dotenv_values('.env')['DB_HOST']
    db = dotenv_values('.env')['DB_NAME']
    return create_engine(f"postgresql://{user}:{password}@{host}/{db}")
