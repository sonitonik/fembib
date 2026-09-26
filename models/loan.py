from database.db import Base
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship


#Spezifikation der Loan-Klasse mit den entsprechenden Attributen 
# und Beziehungen zu anderen Modellen
class Loan(Base):
    __tablename__ = 'loans'
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    status = Column(String) # reserved,expired, active, returned, overdue
    reservation_date = Column(Date)
    loan_date = Column(Date)
    due_date = Column(Date)
    return_date = Column(Date)
    is_returned = Column(Boolean)
    extension_count = Column(Integer, default=0)
    notes = Column(String)
    last_reminder_sent = Column(Date)

    user = relationship('User', back_populates='loans')
    book = relationship('Book', back_populates='loans')

