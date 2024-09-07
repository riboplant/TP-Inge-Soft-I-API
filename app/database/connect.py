from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base

from config import DBSettings as settings





def get_engine(user, password, host, port, db):
    url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    if not database_exists(url):
        create_database(url)
    engine = create_engine(url, pool_size=10, echo=False)
    return engine

def get_engine_from_settings():
    return get_engine(settings.user, settings.password, settings.host, settings.port, settings.name)

def get_session():
    engine = get_engine_from_settings()
    session = sessionmaker(bind=engine)()
    return session

Base = declarative_base()
engine = get_engine_from_settings()

SessionLocal = sessionmaker( autocommit=False,  autoflush=False,  bind=engine )


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
