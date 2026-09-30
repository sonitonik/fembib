import smtplib
from email.mime.text import MIMEText
from datetime import date, timedelta
from database.db import SessionLocal
from models.loan import Loan
from collections import defaultdict
from dotenv import load_dotenv
import os
from sqlalchemy.orm import joinedload


load_dotenv()

try:
    import streamlit as st
    SMTP_SERVER = st.secrets.get("SMTP_SERVER", os.getenv("SMTP_SERVER", ""))
    SMTP_PORT = int(st.secrets.get("SMTP_PORT", os.getenv("SMTP_PORT", "587")))
    SMTP_USER = st.secrets.get("SMTP_USER", os.getenv("SMTP_USER", ""))
    SMTP_PASSWORD = st.secrets.get("SMTP_PASSWORD", os.getenv("SMTP_PASSWORD", ""))
except Exception:
    SMTP_SERVER = os.getenv("SMTP_SERVER", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")


def send_mail(to_adress: str, subject: str, body: str):
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = to_adress

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, to_adress, msg.as_string())


def mail_reminder():
     session = SessionLocal()
     today = date.today()
     cutoff_overdue = today - timedelta(days=7)
     cutoff_predue = today + timedelta(days=5)

     try: 
          predue_loans = (session.query(Loan)
                          .filter(Loan.status.in_(['active']))
                          .filter(Loan.due_date <= cutoff_predue)
                          .filter(Loan.last_reminder_sent == None)
                          .options(joinedload(Loan.book),
                                   joinedload(Loan.user))
                          .all())
          user_predue = defaultdict(list)

          for loan in predue_loans:
              user_predue[loan.user].append((loan, loan.book.title, loan.due_date))

          for user, loan_books in user_predue.items():
              book_list = '\n'.join(
                  f"- {title} (fällig am {due.strftime('%d.%m.%Y')})"
                  for _, title, due in loan_books
              )
              body = (
                  f'Liebe Nutzer:in {user.name}, \n\n'
                  f'wir möchten Dich daran erinnern, dass folgende Bücher bald zurückgegeben werden müssen: \n\n'
                  f'{book_list}\n\n'
                  f'Bitte gib diese rechtzeitig zurück. \n\n'
                  f'Lesegrüße von deiner FemBib'
              )
              send_mail(
                  to_adress = user.mail,
                  subject = 'Erinnerung: Bücher bald fällig',
                  body = body
              )
              for loan, _, _ in loan_books:
                  loan.last_reminder_sent = today
    

          overdue_loans = (session.query(Loan)
                           .filter(Loan.status.in_(['overdue']))
                           .filter((Loan.last_reminder_sent == None) | 
                                   (Loan.last_reminder_sent <= cutoff_overdue))
                           .options(joinedload(Loan.book), 
                                    joinedload(Loan.user))
                           .all())
          
          user_overdue = defaultdict(list)

          for loan in overdue_loans:
              user_overdue[loan.user].append((loan, loan.book.title, loan.due_date))

          for user, loan_books in user_overdue.items():
              book_list = '\n'.join(f'- {title}' for _, title in loan_books)
              body = (
                  f'Liebe Nutzer:in {user.name}, \n\n'
                  f'wir möchten Dich daran erinnern, dass folgende Bücher überfällig sind:\n\n'
                  f'{book_list}\n\n'
                  f'Bitte gib diese so bald wie möglich zurück.\n\n'
                  f'Lesegrüße von deiner FemBib'
                )
              send_mail(to_adress = user.mail, 
                        subject = 'Erinnerung: Überfällige Bücher', 
                        body = body)
              for loan, _ in loan_books:
                  loan.last_reminder_sent = today

          session.commit()


     finally:
         session.close()


if __name__ == "__main__":
    mail_reminder()