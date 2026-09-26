from models.book import Book 
from models.author import Author
from models.user import User
from models.category import Category
from models.tag import Tag
from models.loan import Loan
from database.db import SessionLocal
from sqlalchemy.orm import joinedload

#Book.status: available, reserved, loaned
#Loan.status: reserved, active, returned, overdue


# Buch hinzufügen
def add_book(isbn=None, title=None, author_id=None, category_id=None, 
             tag_ids=None,description=None, status=None,
             pages=None, publication_year=None, added_date=None): 
    session = SessionLocal()
    try:
        if session.query(Book).filter(Book.isbn == isbn).first():
            return
        book = Book(isbn=isbn, title=title, author_id=author_id, 
                    category_id=category_id, 
                    description=description, 
                    status=status, pages=pages, 
                    publication_year=publication_year, added_date=added_date)
        if tag_ids:
            book.tags = session.query(Tag).filter(Tag.id.in_(tag_ids)).all()
        session.add(book)
        session.commit()
    finally: 
        session.close()


# Buch aktualisieren
def update_book(id, title=None, author_id=None, category_id=None, tag_ids=None,
                description=None, isbn=None, status=None,
                pages=None, publication_year=None, added_date=None): 
    session = SessionLocal()
    try:
        query = session.query(Book)
        book = query.filter(Book.id == id).first()
        if title:
            book.title = title
        if author_id: 
            book.author_id = author_id
        if category_id: 
            book.category_id = category_id
        if tag_ids is not None:
            tags = session.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            book.tags = tags
        if description: 
            book.description = description
        if isbn:
            book.isbn = isbn
        if status: 
            book.status = status
        if pages:
            book.pages = pages
        if publication_year: 
            book.publication_year = publication_year
        if added_date: 
            book.added_date = added_date
        session.commit()
    finally:
        session.close()


# Buch löschen
def delete_book(isbn):
    session = SessionLocal()
    try: 
        query = session.query(Book)
        book = query.filter(Book.isbn == isbn).first()
        session.delete(book)
        session.commit()
    finally: 
        session.close()

    
def update_book_status(isbn, status):
    session = SessionLocal()
    try:
        query = session.query(Book)
        book = query.filter(Book.isbn == isbn).first()
        book.status = status
        if status == 'available':
            loan = session.query(Loan).filter(Loan.book_id == book.id, 
                                        Loan.status != 'returned').first()
            if loan: 
                loan.status = 'returned'
        if status == 'reserved':
            loan = session.query(Loan).filter(Loan.book_id == book.id, 
                                            Loan.status != 'reserved').first()
            if loan:
                loan.status = 'reserved'
        if status == 'loaned': 
            loan = session.query(Loan).filter(Loan.book_id == book.id,
                                            Loan.status != 'active').first()
            if loan: 
                loan.status = 'active'
        session.commit()
    finally:
        session.close()
    

# Autor:in hinzufügen
def add_author(name, biography, birth_year, death_year=None): 
    session = SessionLocal()
    try:
        if session.query(Author).filter(Author.name == name).first(): 
            return
        author = Author(name=name, 
                        biography=biography, 
                        birth_year=int(birth_year), 
                        death_year=int(death_year) if death_year else None)
        session.add(author)
        session.commit()
    finally:
        session.close()


# Autor:in aktualisieren
def update_author(author_id, name=None, biography=None, 
                  birth_year=None, death_year=None):
    session = SessionLocal()
    try: 
        query = session.query(Author)
        author = query.filter(Author.id == author_id).first()
        if name:
            author.name = name
        if biography: 
            author.biography = biography
        if birth_year: 
            author.birth_year = birth_year
        if death_year: 
            author.death_year = death_year
        session.commit()
    finally: 
        session.close()
        

# Autor:in löschen
def delete_author(author_id):
    session = SessionLocal()
    try:
        query = session.query(Author)
        author = query.filter(Author.id == author_id).first()
        session.delete(author)
        session.commit()
    finally:
        session.close()


# Autor:in anhand des Namens abrufen
def get_author_by_name(name):
    session = SessionLocal()
    try:
        return session.query(Author).filter(Author.name == name).first()
    finally:
        session.close()


# Kategorie hinzufügen
def add_category(name, description): 
    session = SessionLocal()
    try:
        if session.query(Category).filter(Category.name == name).first():
            return
        category = Category(name=name, description=description)
        session.add(category)
        session.commit()
    finally: 
        session.close()


# Kategorie aktualisieren
def update_category(category_id, name=None, description=None):
    session = SessionLocal()
    try: 
        query = session.query(Category)
        category = query.filter(Category.id == category_id).first()
        if name:
            category.name = name
        if description:
            category.description = description
        session.commit()
    finally:
        session.close()
        

# Kategorie löschen
def delete_category(category_id):
    session = SessionLocal()
    try:
        query = session.query(Category)
        category = query.filter(Category.id == category_id).first()
        session.delete(category)
        session.commit()
    finally:
        session.close()


# Tag hinzufügen
def add_tag(name):
    session = SessionLocal()
    try:
        if session.query(Tag).filter(Tag.name == name).first():
            return
        tag = Tag(name=name)
        session.add(tag)
        session.commit()
    finally: 
        session.close()


# Tag aktualisieren
def update_tag(tag_id, name=None):
    session = SessionLocal()
    try: 
        query = session.query(Tag)
        tag = query.filter(Tag.id == tag_id).first()
        if name:
            tag.name = name
        session.commit()
    finally:
        session.close()


# Tag löschen
def delete_tag(tag_id):
    session = SessionLocal()
    try:
        query = session.query(Tag)
        tag = query.filter(Tag.id == tag_id).first()
        session.delete(tag)
        session.commit()
    finally:
        session.close()


# Nutzer:in hinzufügen
def add_user(name, mail, password_hash):
    session = SessionLocal()
    try:
        if session.query(User).filter(User.name == name).first():
            return
        user = User(name=name, password_hash=password_hash, mail=mail)
        session.add(user)
        session.commit()
    finally: 
        session.close()


# Nutzer:in aktualisieren
def update_user(user_id, name=None, mail=None, password_hash=None, 
                is_admin=None):
    session = SessionLocal()
    try: 
        query = session.query(User)
        user = query.filter(User.id == user_id).first()
        if name:
            user.name = name
        if mail:
            user.mail = mail
        if password_hash:
            user.password_hash = password_hash
        if is_admin: 
            user.is_admin = is_admin
        session.commit()
    finally:
        session.close()


# Nutzer:in löschen
def delete_user(user_id):
    session = SessionLocal()
    try:
        query = session.query(User)
        user = query.filter(User.id == user_id).first()
        session.delete(user)
        session.commit()
    finally:
        session.close()


# Nutzer:in anhand der ID abrufen
def get_user_by_id(user_id):
    session = SessionLocal()
    try:
        return (session.query(User)
                .options(joinedload(User.categories), joinedload(User.tags))
                .filter(User.id == user_id).first())
    finally:
        session.close()


# Alle Nutzer:innen abrufen
def get_all_users():
    session = SessionLocal()
    try:
        return session.query(User).all()
    finally:
        session.close()
