from database.db import Base
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship


#Spezifikation der Author-Klasse mit den entsprechenden Attributen 
# und Beziehungen zu anderen Modellen
class Author(Base): 
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    biography = Column(Text)
    birth_year = Column(Integer)
    death_year = Column(Integer)

    books = relationship('Book', back_populates='author')
