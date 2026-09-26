from database.db import Base
from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from models.associations import book_tags


#Spezifikation der Book-Klasse mit den entsprechenden Attributen 
# und Beziehungen zu anderen Modellen
class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author_id = Column(Integer, ForeignKey('authors.id'))
    isbn = Column(String)
    category_id = Column(Integer, ForeignKey('categories.id'))
    description = Column(Text)
    pages = Column(Integer)
    publication_year = Column(Integer)
    status = Column(String) # available, reserved, loaned
    added_date = Column(Date)

    tags = relationship('Tag', secondary='book_tags', back_populates='books')
    author = relationship('Author', back_populates='books')
    category = relationship('Category', back_populates='books')
    loans = relationship('Loan', back_populates='book')





