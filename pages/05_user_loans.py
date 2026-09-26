import streamlit as st
from services.loan_service import (extend_loan, get_user_active_loans, 
                                   get_user_active_reservations, 
                                   cancel_reservation)
from services.book_service import get_book_by_id
from datetime import date
from utilities.ui import hide_sidebar


st.set_page_config(page_title='FemLib - Meine Ausleihen', page_icon='📚', 
                   layout='wide', initial_sidebar_state='collapsed')

hide_sidebar()

# Zugriffsschutz
if 'user' not in st.session_state or not st.session_state.user:
    st.switch_page('homepage.py')

if st.button('← Zurück zum Katalog'):
    st.switch_page('homepage.py')

st.title('📋 Meine Ausleihen')

user = st.session_state.user
active_loans = get_user_active_loans(user.id)
active_reservations = get_user_active_reservations(user.id)
loans = active_loans + active_reservations

if not loans:
    st.info('Du hast aktuell keine Reservierungen oder Ausleihen. 📚')
else:
    # Reservierungen und aktive Ausleihen in separaten Abschnitten anzeigen
    if active_reservations:
        st.subheader('🔖 Reservierungen')
        for reservation in active_reservations:
            book = get_book_by_id(reservation.book_id)

            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([4, 2, 2, 1])
                with col1:
                    st.markdown(f'**{book.title if book else 'Unbekannt'}**')
                with col2:
                    days = ((date.today() - reservation.reservation_date)
                            .days if reservation.reservation_date else 0)
                    remaining = 7 - days
                    if remaining <= 0:
                        st.warning(f'⚠️ Abgelaufen')
                    else:
                        st.caption(f'Noch {remaining} Tage gültig')
                with col3:
                    date_str = (reservation.reservation_date.strftime('%d.%m.%Y')
                                if reservation.reservation_date else '-')
                    
                    st.caption(f'Reserviert am: {date_str}')
                            
                with col4:
                    if st.button('❌', key=f'cancel_{reservation.id}'):
                        cancel_reservation(reservation.id)
                        st.rerun()

    if active_loans:
        st.subheader('📖 Aktive Ausleihen')
        for loan in active_loans:
            book = get_book_by_id(loan.book_id)

            with st.container(border=True):
                col1, col2, col3 = st.columns([4, 2, 2])
                with col1:
                    st.markdown(f'**{book.title if book else 'Unbekannt'}**')
                with col2:
                    if loan.due_date:
                        if loan.status == 'overdue':
                            st.error(f'⚠️ Überfällig seit '
                                     f'{loan.due_date.strftime('%d.%m.%Y')}')
                        else:
                            st.caption(f'Fällig: '
                                       f'{loan.due_date.strftime('%d.%m.%Y')}')
                with col3:
                    if loan.status != 'overdue':
                        if (loan.extension_count < loan.max_extensions 
                            if loan.max_extensions else True):
                            if st.button('🔄 Verlängern', 
                                         key=f'extend_{loan.id}'):
                                extend_loan(loan.id)
                                st.rerun()
                        else:
                            st.caption('Max. Verlängerungen erreicht')