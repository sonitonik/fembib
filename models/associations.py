from database.db import Base
from sqlalchemy import Column, Integer, String, Table, ForeignKey


book_tags = Table(
    'book_tags',
    Base.metadata, 
    Column('book_id', Integer, ForeignKey('books.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

user_categories = Table(
    'user_categories',
    Base.metadata, 
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), 
           primary_key=True)
)

user_tags = Table(
    'user_tags',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)