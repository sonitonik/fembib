from database.db import SessionLocal
from models.user import User
from sqlalchemy.orm import joinedload
from services.mail_service import send_mail
import bcrypt
import secrets

APP_URL = 'https://fembib-subbotnik.streamlit.app'


# Funktion für die Registrierung von Nutzer:innen
def register_user(username, password, mail):
    session = SessionLocal()
    try:
        #Prüfe ob User:in existiert
        if session.query(User).filter(User.mail == mail).first():
            return False
        if session.query(User).filter(User.name == username).first():
            return False

        #Passwort-Hash
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), 
                                        bcrypt.gensalt())

        token = secrets.token_urlsafe(32)

        #Neue User:in erstellen und speichern
        new_user = User(name=username, mail=mail, 
                        password_hash=hashed_password.decode('utf-8'), 
                        confirmed = False,
                        confirmation_token = token)
        session.add(new_user)
        session.commit()
        

        confirm_url = f'{APP_URL}/?token={token}'
        body = (
            f'Hallo {username}, \n\n'
            f'bitte bestätige Deine E-Mail-Adresse: \n\n'
            f'{confirm_url}\n\n'
            f'Lesegrüße von deiner FemBib'
        )
        send_mail(mail, 'Bitte bestätige deine E-Mail', body)

        return True, None
    
    finally:
        session.close()

def confirm_mail(token: str) -> bool:
    session = SessionLocal()
    
    try:
        user = session.query(User).filter(User.confirmation_token == token).first()
        if user:
            user.confirmed = True
            user.confirmation_token = None
            session.commit()
            return True
        return False

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
        if user and user.confirmed and bcrypt.checkpw(password.encode('utf-8'), 
                                   user.password_hash.encode('utf-8')):
            return user
        else:
            return None
    finally:
        session.close()

