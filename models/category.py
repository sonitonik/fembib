from database.db import Base
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship


#Spezifikation der Category-Klasse mit den entsprechenden Attributen 
# und Beziehungen zu anderen Modellen
class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)

    books = relationship('Book', back_populates='category')
