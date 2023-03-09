from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..utils.env_vars import POSTGRES_URI


engine = create_engine(POSTGRES_URI, echo=True)

Base = declarative_base()

SessionLocal = sessionmaker(bind=engine)