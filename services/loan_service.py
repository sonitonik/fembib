from database.db import SessionLocal
from models.book import Book
from models.loan import Loan
from datetime import date, timedelta


#Book.status: available, reserved, loaned
#Loan.status: reserved, expired, active, returned, overdue

# Geschäftsregeln für die Verwaltung von Ausleihen 
# und Reservierungen von Büchern
max_extensions = 3
max_loans = 3
reservation_expiry_days = 7
loan_duration_days = 42


# Funktion für die Verwaltung von Reservierungen von Büchern
def reserve_book(book_id, user_id, notes=None):
    session = SessionLocal()
    try:
        if session.query(Loan).filter(Loan.book_id == book_id, 
                                      Loan.status == 'reserved').first():
                return
        if session.query(Loan).filter(Loan.book_id == book_id, 
                                           Loan.status == 'active').first():
                return
        reservation_date = date.today()
        status = 'reserved'
        book = session.query(Book).filter(Book.id == book_id).first()
        book.status = 'reserved'
        reservation = Loan(book_id=book_id, user_id=user_id, status=status, 
                           reservation_date=reservation_date, notes=notes)
        session.add(reservation)
        session.commit()
    finally: 
        session.close()


# Funktion ür die Verwaltung von Ausleihen von Büchern
def checkout_book(book_id, user_id, notes=None):
    session = SessionLocal()
    try:
#Prüfen, ob Buch schon verliehen:
        if existing_loan := (session.query(Loan)
                             .filter(Loan.book_id == book_id, 
                                     Loan.status == 'active')
                             .first()):
                return
        
#Prüfen, ob Buch von einer anderen Person reserviert ist:
        if existing_reservation := (session.query(Loan)
                                    .filter(Loan.book_id == book_id, 
                                            Loan.status == 'reserved', 
                                            Loan.user_id != user_id)
                                    .first()):
                if (date.today() - existing_reservation.reservation_date 
                    > timedelta(reservation_expiry_days)):
                      existing_reservation.status = 'expired'
                      book = (session.query(Book).
                              filter(Book.id == book_id)
                              .first())
                      book.status = 'available'
                else: 
                     return
                
# Prüfe die Anzahl der Ausleihen der User:in:
        if (len(session.query(Loan)
                .filter(Loan.user_id == user_id,
                        Loan.status == 'active').all()) >= max_loans):
            return
        
#Ausleihe verbuchen:
        if loan := session.query(Loan).filter(Loan.book_id == book_id, 
                                      Loan.status == 'reserved', 
                                      Loan.user_id == user_id).first():
                loan_date = date.today()
                loan.loan_date = loan_date
                due_date = loan_date + timedelta(days=42)
                loan.due_date = due_date
                status = 'active'
                loan.status = status
                book = session.query(Book).filter(Book.id == book_id).first()
                book.status = 'loaned'
        elif (book := session.query(Book).filter(Book.id == book_id, 
                                       Book.status == 'available').first()):
                loan = Loan(book_id=book_id, user_id=user_id, notes=notes)
                loan_date = date.today()
                loan.loan_date = loan_date
                due_date = loan_date + timedelta(days=42)
                loan.due_date = due_date
                status = 'active'
                loan.status = status
                book.status = 'loaned'
        session.add(loan)
        session.commit()
    finally:
        session.close()


# Funktion für die Verwaltung von Rückgaben von Büchern
def return_book(loan_id, book_id):
    session = SessionLocal()
    try:
        loan = session.query(Loan).filter(Loan.id == loan_id).first()
        loan.status = 'returned'
        book = session.query(Book).filter(Book.id == book_id).first()
        book.status = 'available'
        loan.return_date = date.today()
        session.commit()
    finally:
        session.close()
    

# Funktion für die Verwaltung von Verlängerungen von Ausleihen  
def extend_loan(loan_id):
    session = SessionLocal()
    try:
        loan = session.query(Loan).filter(Loan.id == loan_id).first()
        if loan.extension_count < max_extensions: 
             loan.due_date = loan.due_date + timedelta(loan_duration_days)
             loan.extension_count += 1
        else:
             return
        session.commit()
    finally:
        session.close()


#Funktion für die Überprüfung von überfälligen Ausleihen    
def is_overdue(loan_id):
    session = SessionLocal()
    try:
        loan = session.query(Loan).filter(Loan.id == loan_id).first()
        if date.today() > loan.due_date:
             loan.status = 'overdue'
             session.commit()
             return True
        return False
    finally:
        session.close()
    

#Funktion für die Anzeige aktiver und überzogener Ausleihen eines Users
def get_user_active_loans(user_id): 
    session = SessionLocal()
    try: 
        active_loans = (session.query(Loan)
                 .filter(Loan.user_id == user_id, 
                         Loan.status.in_(['active', 'overdue'])).all())
        return active_loans
    finally: 
        session.close()

#Funktion für die Anzeige von aktiver und abgelaufener 
# Reservierungen eines Users
def get_user_active_reservations(user_id): 
    session = SessionLocal()
    try: 
        reservations = (session.query(Loan)
                 .filter(Loan.user_id == user_id, 
                         Loan.status.in_(['reserved'])).all())
        return reservations
    finally: 
        session.close()


# Funktion für die Verwaltung von Stornierungen von Reservierungen
def cancel_reservation(reservation_id):
    session = SessionLocal()
    try:
        loan = session.query(Loan).filter(Loan.id == reservation_id).first()
        loan.status = 'expired'
        book = session.query(Book).filter(Book.id == loan.book_id).first()
        book.status = 'available'
        session.commit()
    finally:
        session.close()


# Funktion für die Anzeige aller aktiven Reservierungen
def get_all_active_reservations():
    session = SessionLocal()
    try:
        return session.query(Loan).filter(Loan.status == 'reserved').all()
    finally:
        session.close()


# Funktion für die Anzeige aller aktiven und überzogenen Ausleihen
def get_all_active_loans():
    session = SessionLocal()
    try:
        return (session.query(Loan)
                .filter(Loan.status.in_(['active', 'overdue'])).all())
    finally:
        session.close()
          
