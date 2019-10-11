import os

SQLALCHEMY_DATABASE_URI = (
    f'postgresql://'
    f'{os.environ["POSTGRES_USER"]}:'
    f'{os.environ["POSTGRES_PASSWORD"]}@'
    f'{os.environ["POSTGRES_HOST"]}:'
    f'{os.environ.get("POSTGRES_PORT", 5432)}/'
    f'{os.environ["POSTGRES_DB_NAME"]}'
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = True
