import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from dotenv import load_dotenv
load_dotenv()

# Ambil URL database dari environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("Environment variable DATABASE_URL belum diset!")

# Engine koneksi
engine = create_engine(DATABASE_URL, echo=True)

# Session untuk query
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base untuk model ORM
Base = declarative_base()

# Dependency untuk session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
