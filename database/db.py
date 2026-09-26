import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Laden der Umgebungsvariablen und Einrichten der Datenbankverbindung
load_dotenv(override=True)
DATABASE_URL = os.environ.get('DATABASE_URL')
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind = engine, autocommit = False, 
                            autoflush = False)

