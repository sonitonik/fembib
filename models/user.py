from database.db import Base
from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from models.associations import user_categories, user_tags


#spezifikation der User-Klasse mit den entsprechenden Attributen
# und Beziehungen zu anderen Modellen
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    mail = Column(String)
    password_hash = Column(String)
    is_admin = Column(Boolean, default=False)
    confirmed = Column(Boolean, default=False)
    confirmation_token = Column(Text)

    categories = relationship('Category', secondary='user_categories')
    tags = relationship('Tag', secondary='user_tags')
    loans = relationship('Loan', back_populates='user')