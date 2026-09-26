from database.db import SessionLocal
from models.user import User
from sqlalchemy.orm import joinedload
import bcrypt


# Funktion für die Registrierung von Nutzer:innen
def register_user(username, password, mail):
    session = SessionLocal()
    try:
        #Prüfe ob User:in existiert
        if session.query(User).filter(User.mail == mail).first():
            return
        if session.query(User).filter(User.name == username).first():
            return

        #Passwort-Hash
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), 
                                        bcrypt.gensalt())

        #Neue User:in erstellen und speichern
        new_user = User(name=username, mail=mail, 
                        password_hash=hashed_password.decode('utf-8'))
        session.add(new_user)
        session.commit()
    finally:
        session.close()


# Funktion für die Anmeldung von Nutzer:innen
def login(mail, password):
    session = SessionLocal()
    try:
        user = (session.query(User)
                .options(joinedload(User.categories), 
                         joinedload(User.tags))
                .filter(User.mail == mail)
                .first())
        if user and bcrypt.checkpw(password.encode('utf-8'), 
                                   user.password_hash.encode('utf-8')):
            return user
        else:
            return None
    finally:
        session.close()

