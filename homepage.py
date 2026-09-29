import streamlit as st
from services.auth_service import login, register_user
from services.book_service import (get_all_books, search_books, 
                                   get_all_categories, get_all_authors, 
                                   get_all_tags)
from services.loan_service import reserve_book
from itertools import zip_longest
from utilities.ui import hide_sidebar
import json

st.set_page_config(page_title='FemBib', page_icon='📚', 
                   layout='wide')

hide_sidebar()

token = st.query_params.get('token')
if token:
    if confirm_mail(token):
        st.success('E-Mail bestätigt. Du kannst Dich jetzt anmelden.')
    else:
        st.error('Ungültige E-Mail.')

def load_language(lang):
    with open(f"{lang}.json", encoding = "utf-8") as f:
        return json.load(f)

# Session State initialisieren
if 'user' not in st.session_state:
    st.session_state.user = None


# Sprachauswahl initialisieren für die Benutzer:innenoberfläche
if "language" not in st.session_state:
    st.session_state.language = "de"


def tr(key):
        translations = load_language(st.session_state.language)
        return translations.get(key,key)


# Login Dialog
@st.dialog(tr('login_title'))
def show_login():
    tab1, tab2 = st.tabs([tr('login_tab'), tr('register_tab')])
    
    with tab1:
        mail = st.text_input(tr('email'), key='login_mail')
        password = st.text_input(tr('password'), type='password', 
                                 key='login_password')
        if st.button(tr('login_button'), use_container_width=True):
            user = login(mail, password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error(tr('login_failed'))
    
    with tab2:
        registration_name = st.text_input(tr('name'), key='registration_name')
        registration_mail = st.text_input(tr('email'), key='registration_mail')
        registration_password = st.text_input(tr('password'), type='password', 
                                              key='registration_password')
        registration_password_confirm = st.text_input(tr('password_confirm'), 
                                                      type = 'password',
                                                      key = 'registration_password_confirm')
        if st.button(tr('register_button'), use_container_width=True):
            if registration_password.strip() != registration_password_confirm.strip():
                st.error(tr('password_mismatch'))
            else:
                if register_user(registration_name, registration_password, 
                          registration_mail) is True:
                    st.success(tr('register_success'))
                else:
                    st.error(tr('register_failure'))

#Header
col1, col2, col3, col4, col5 = st.columns([5, 2, 2, 1, 1])
with col1:
    st.title(tr('title'))
#with col2:
    #if st.session_state.user and not st.session_state.user.is_admin:
        #if st.button(tr('recommendations')):
            #st.switch_page('pages/03_recommendations.py')
with col3:
    if st.session_state.user and not st.session_state.user.is_admin:
        if st.button(tr('my_loans')):
            st.switch_page('pages/05_user_loans.py')
    elif st.session_state.user and st.session_state.user.is_admin:
        if st.button(tr('admin')):
            st.switch_page('pages/04_admin.py')
with col4:
    if st.session_state.user:
        if st.button(tr('logout')):
            st.session_state.user = None
            st.rerun()
    else:
        if st.button(tr('login')):
            show_login()
with col5: 
    st.selectbox("DE/EN", ["de", "en"], key = "language")


# Suche & Filter
search_query = st.text_input(tr('search_label'), 
                             placeholder=(tr('search_placeholder')))

col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

categories = get_all_categories()
authors = get_all_authors()
tags = get_all_tags()

with col1:
    selected_category = st.selectbox(tr('all_categories'), [tr('all_categories')] +
                                     [c.name for c in categories])
with col2:
    selected_author = st.selectbox(tr('all_authors'), [tr('all_authors')] +
                                   [a.name for a in authors])
with col3:
    selected_tag = st.selectbox(tr('all_tags'), [tr('all_tags')] +
                                [t.name for t in tags])
with col4:
    only_available = st.checkbox(tr('available_only'))

# Bücher laden
books = search_books(
    title=search_query if search_query else None,
    author=selected_author if selected_author!='Alle Autor:innen' else None,
    category=(selected_category if selected_category!='Alle Kategorien' 
              else None),
    tag = selected_tag if selected_tag!='Alle Tags' else None
)

if only_available:
    books = [b for b in books if b.status == 'available']

st.caption(tr(f'{len(books)} results'))

# Buchliste Spaltenweise anzeigen
left_books = books[:(len(books)//2)]
right_books = books[(len(books)//2):]

for left_book, right_book in zip_longest(left_books, right_books): 
    col1, col2, col3, col4 = st.columns([1, 3, 1, 3])

    if left_book:
        with col1:
            st.markdown('<p style="font-size: 60px;">📕</p>', 
                        unsafe_allow_html=True)
        with col2:
            st.markdown(f'**{left_book.title}**')
            author_name = (left_book.author.name 
                        if left_book.author else tr('unknown_author'))
            category_name = (left_book.category.name 
                             if left_book.category else '')
            st.caption(f'{author_name} · {category_name}')
                
            # Tags
            tag_str = ' '.join([f'`{t.name}`' for t in left_book.tags])
            if tag_str:
                st.markdown(tag_str)
                
            # Status & Reservieren
            col_status, col_btn = st.columns([1, 1])
            with col_status:
                if left_book.status == 'available':
                    st.success(tr('status_available'))
                elif left_book.status == 'reserved':
                    st.warning(tr('status_reserved'))
                else:
                    st.error(tr('status_borrowed'))
                
            with col_btn:
                if left_book.status == 'available':
                    if st.button(tr('reserve'), 
                                 key=f'reserve_{left_book.id}'):
                        if st.session_state.user:
                            reserve_book(left_book.id, 
                                         st.session_state.user.id)
                            st.rerun()
                        else:
                            show_login()
                if st.button(tr('details'), key=f'details_{left_book.id}'):
                    st.session_state.selected_book_id = left_book.id
                    st.switch_page('pages/02_book_details.py')

    if right_book:
        with col3:
            st.markdown('<p style="font-size: 60px;">📕</p>', 
                        unsafe_allow_html=True)
        with col4:
            st.markdown(f'**{right_book.title}**')
            author_name = (right_book.author.name 
                        if right_book.author else tr('unknown_author'))
            category_name = (right_book.category.name 
                             if right_book.category else '')
            st.caption(f'{author_name} · {category_name}')
                
            # Tags
            tag_str = ' '.join([f'`{t.name}`' for t in right_book.tags])
            if tag_str:
                st.markdown(tag_str)
                
            # Status & Reservieren
            col_status, col_btn = st.columns([1, 1])
            with col_status:
                if right_book.status == 'available':
                    st.success(tr('status_available'))
                elif right_book.status == 'reserved':
                    st.warning(tr('status_reserved'))
                else:
                    st.error(tr('status_borrowed'))
                
            with col_btn:
                if right_book.status == 'available':
                    if st.button(tr('reserve'), 
                                 key=f'reserve_{right_book.id}'):
                        if st.session_state.user:
                            reserve_book(right_book.id, 
                                         st.session_state.user.id)
                            st.rerun()
                        else:
                            show_login()
                if st.button(tr('details'), key=f'details_{right_book.id}'):
                    st.session_state.selected_book_id = right_book.id
                    st.switch_page('pages/02_book_details.py')