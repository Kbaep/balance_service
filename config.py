from sqlalchemy import create_engine
import os


def get_session():
    POSTGRES_DB = os.environ.get('POSTGRES_DB')
    POSTGRES_USER = os.environ.get('POSTGRES_USER')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
    POSTGRES_PORT = os.environ.get('POSTGRES_PORT')
    engine = create_engine(
        f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}')  # База Postgres
    # База sqlite
    # engine = create_engine('sqlite:///db.sqlite')
    return engine
