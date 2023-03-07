from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..utils.env_vars import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASS, POSTGRES_NAME


DATABASE_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASS}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_NAME}'

engine = create_engine(DATABASE_URI, echo=True)

Base = declarative_base()

SessionLocal = sessionmaker(bind=engine)