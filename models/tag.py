from database.db import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.associations import book_tags


#Spezifikation der Tag-Klasse mit den entsprechenden Attributen 
# und Beziehungen zu anderen Modellen
class Tag(Base):
    __tablename__= 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    books = relationship('Book', secondary = 'book_tags', 
                         back_populates='tags')


