# database/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base
from database.base import Base  


# Use the same name everywhere
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:dev2003@localhost:3306/bitewise_db"

# engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This Base will be shared across all of your models
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
