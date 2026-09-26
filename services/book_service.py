from database.db import SessionLocal
from models.book import Book
from models.author import Author
from models.category import Category
from models.tag import Tag
from sqlalchemy.orm import joinedload


# Funktion zum Abrufen aller Bücher in der Datenbank
def get_all_books():
    session = SessionLocal()
    try:
        return (session.query(Book)
                .options(joinedload(Book.author), 
                         joinedload(Book.category), 
                         joinedload(Book.tags)).all())
    finally:
        session.close()


# Funktion zum Abrufen eines Buches anhand seiner ID
def get_book_by_id(id):
    session = SessionLocal()
    try: 
        return (session.query(Book)
                .options(joinedload(Book.category),
                         joinedload(Book.tags), 
                         joinedload(Book.author))
                .filter(Book.id == id)
                .first())
    finally: 
        session.close()


# Funktion zum Abrufen eines Buches anhand seines Titels
def get_book_by_title(title):
    session = SessionLocal()
    try: 
        return (session.query(Book)
                .options(joinedload(Book.category),
                         joinedload(Book.tags), 
                         joinedload(Book.author))
                .filter(Book.title == title)
                .first())
    finally: 
        session.close()


# Suchfunktion für Bücher basierend auf Titel, Autor:in, Kategorie oder Tag
def search_books(title=None, author=None, category=None, tag=None):
    session = SessionLocal()
    try: 
        query = session.query(Book).options(joinedload(Book.author), 
                                            joinedload(Book.category), 
                                            joinedload(Book.tags))
        if title:
            query = query.filter(Book.title.ilike(f'%{title}%'))
        if author: 
            query = (query.join(Book.author)
                     .filter(Author.name.ilike(f'%{author}%')))
        if category: 
            query = (query.join(Book.category)
                     .filter(Category.name.ilike(f'%{category}%')))
        if tag:
            query = query.join(Book.tags).filter(Tag.name.ilike(f'%{tag}%'))
        return query.order_by(Book.id).all()
    finally: 
        session.close()


# Funktion zum Abrufen des Status eines Buches anhand der ISBN
def get_book_status(isbn): 
    session = SessionLocal()
    try:
        query = session.query(Book)
        book = query.filter(Book.isbn == isbn).first()
        return book.status
    finally:
        session.close()


# Funktion zum Abrufen aller Autor:innen
def get_all_authors():
    session = SessionLocal()
    try:
        return session.query(Author).all()
    finally:
        session.close()


# Funktion zum Abrufen aller Kategorien
def get_all_categories():
    session = SessionLocal()
    try:
        return session.query(Category).all()
    finally:
        session.close()


# Funktion zum Abrufen aller Tags
def get_all_tags():
    session = SessionLocal()
    try:
        return session.query(Tag).all()
    finally:
        session.close()


