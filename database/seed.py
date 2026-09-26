from database.db import SessionLocal, Base, engine
from models.user import User
from models.category import Category
from models.tag import Tag
from models.loan import Loan
from models.book import Book
from models.author import Author
from dotenv import load_dotenv
import bcrypt
import os


# Hilfsfunktion, um Umgebungsvariablen zu laden und Admin-Daten zu extrahieren
def load_env():
    load_dotenv()
    admin_mail = os.getenv("ADMIN_MAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin_name = os.getenv("ADMIN_NAME")
    return admin_mail, admin_password, admin_name


# Funktion zum Erstellen der Tabellen in der Datenbank
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tabellen erfolgreich erstellt!")
   

# Funktion zum Erstellen eines Admin-Users, falls dieser noch nicht existiert
def create_admin_user():
    session = SessionLocal()
    try:
        admin_mail, admin_password, admin_name = load_env()
        if session.query(User).filter(User.mail == admin_mail).first():
            print("Admin existiert bereits.")
            return
        hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), 
                                        bcrypt.gensalt())
        admin_user = User(mail=admin_mail, 
                          password_hash=hashed_password.decode('utf-8'),
                          is_admin=True,
                          name=admin_name)
        session.add(admin_user)
        session.commit()
        print("Admin erfolgreich erstellt!")
    finally:
        session.close()
        

if __name__ == '__main__':
    create_tables()
    create_admin_user()