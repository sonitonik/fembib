import streamlit as st
from services.book_service import get_book_by_id
from services.loan_service import reserve_book
from utilities.ui import hide_sidebar


st.set_page_config(page_title='FemLib - Buchdetails', page_icon='📚', 
                   layout='wide', initial_sidebar_state='collapsed')

hide_sidebar()

if 'user' not in st.session_state:
    st.session_state.user = None

# Buchdetails aus Session State laden
if ('selected_book_id' not in st.session_state 
    or not st.session_state.selected_book_id):
    st.warning('Kein Buch ausgewählt.')
    if st.button('← Zurück zum Katalog'):
        st.switch_page('homepage.py')
    st.stop()

book = get_book_by_id(st.session_state.selected_book_id)

if not book:
    st.error('Buch nicht gefunden.')
    st.stop()

# Zurück-Button
if st.button('← Zurück zum Katalog'):
    st.switch_page('homepage.py')

st.divider()

col1, col2 = st.columns([1, 3])

with col1:
    st.markdown('## 📕')

with col2:
    st.title(book.title)
    
    author = book.author
    category = book.category

    if author:
        st.markdown(f'**Autorin:** {author.name}')
    if category:
        st.markdown(f'**Kategorie:** {category.name}')
    if book.isbn:
        st.markdown(f'**ISBN:** {book.isbn}')
    if book.publication_year:
        st.markdown(f'**Erscheinungsjahr:** {book.publication_year}')
    if book.pages:
        st.markdown(f'**Seiten:** {book.pages}')
    
    # Tags
    if book.tags:
        tag_str = ' '.join([f'`{t.name}`' for t in book.tags])
        st.markdown(f'**Tags:** {tag_str}')
    
    # Status & Reservieren
    st.divider()
    if book.status == 'available':
        st.success('✅ Verfügbar')
        if st.session_state.user:
            if st.button('🔖 Reservieren', key=f'reserve_{book.id}'):
                reserve_book(book.id, st.session_state.user.id)
                st.rerun()
        else:
            st.warning('Zum Reservieren bitte anmelden.')
    elif book.status == 'reserved':
        st.warning('🔖 Reserviert')
    
    else:
        st.error('❌ Nicht verfügbar')

# Beschreibung
if book.description:
    st.divider()
    st.subheader('Beschreibung')
    st.write(book.description)