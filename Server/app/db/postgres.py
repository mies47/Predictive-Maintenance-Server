import os
from dotenv import load_dotenv

from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_HOSTNAME = os.getenv('POSTGRES_HOST')
DB_PORT = os.getenv('POSTGRES_PORT')
DB_NAME = os.getenv('POSTGRES_DB')


engine = create_engine(f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOSTNAME}:{DB_PORT}/{DB_NAME}',
    echo=True
)

Base = declarative_base()

SessionLocal = sessionmaker(bind=engine)