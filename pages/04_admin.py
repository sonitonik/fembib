import streamlit as st
from services.admin_service import (add_book, add_author, update_book, 
                                    delete_book, 
                                    delete_user, get_all_users, update_user,
                                    get_user_by_id)
from services.loan_service import (checkout_book, return_book, 
                                   get_all_active_reservations,
                                   get_all_active_loans, 
                                   cancel_reservation)
from services.book_service import (get_all_books,
                                   get_book_by_id, get_all_categories, 
                                   get_all_authors, get_all_tags)
from datetime import date
from utilities.ui import hide_sidebar


st.set_page_config(page_title='FemLib Admin', page_icon='📚', 
                   layout='wide', initial_sidebar_state='collapsed')

hide_sidebar()

#Zugriffsschutz
if 'user' not in st.session_state or not st.session_state.user:
   st.switch_page('homepage.py')
if not st.session_state.user.is_admin:
    st.switch_page('homepage.py')


if st.button('← Zurück zum Katalog'):
    st.switch_page('homepage.py')


#Session State
if 'admin_view' not in st.session_state:
    st.session_state.admin_view = 'reservations'
if 'editing_book_id' not in st.session_state:
    st.session_state.editing_book_id = None


#Header
col1, col2 = st.columns([8, 2])
with col1:
    st.title('📚 FemLib')

col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 2, 1])
with col1:
    if st.button('📋 Dashboard'):
        st.session_state.admin_view = 'reservations'
        st.rerun()
with col2:
    if st.button('📕+ Buch hinzufügen'):
        st.session_state.admin_view = 'add_book'
        st.rerun()
with col3:
    if st.button('📚 Bücher verwalten'):
        st.session_state.admin_view = 'manage_books'
        st.rerun()
with col4:
    if st.button('👥 User:innen'):
        st.session_state.admin_view = 'manage_users'
        st.rerun()
with col5:
    if st.button('✍️+ Autor:in hinzufügen'):
        st.session_state.admin_view = 'manage_author'
        st.rerun()
with col6:
    if st.button('Logout'):
        st.session_state.user = None
        st.switch_page('homepage.py')


st.divider()

# Reservierungen & Ausleihen
if st.session_state.admin_view == 'reservations':
    st.header('📋 Offene Reservierungen & Ausleihen')

    reservations = get_all_active_reservations()
    loans = get_all_active_loans()

    if not reservations and not loans:
        st.info('Keine offenen Reservierungen oder Ausleihen vorhanden .')
    else:
        #Erster Teil: Reservierungen
        with st.container(border=True):
            st.subheader('Reservierungen')
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            col1.markdown('**Buch**')
            col2.markdown('**Benutzer:in**')
            col3.markdown('**Datum**')
            col4.markdown('**Aktion**')
            st.divider()
                    
            for loan in reservations:
                book = get_book_by_id(loan.book_id)
                user = get_user_by_id(loan.user_id)
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

                is_expired = ((date.today() - loan.reservation_date).
                                days > 7 if loan.reservation_date else False)

                with col1:
                    title = book.title if book else 'Unbekannt'
                    if is_expired:
                        st.markdown(f'⚠️ {title}')
                    else:
                        st.write(title)
                with col2:
                    st.write(user.name if user else 'Unbekannt')
                with col3:
                    st.write(loan.reservation_date.strftime('%d.%m.%Y') 
                            if loan.reservation_date else '-')
                with col4:
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button('✅', key=f'checkout_{loan.id}'):
                            checkout_book(loan.book_id, loan.user_id)
                            st.rerun()
                                
                    with btn_col2:
                        if st.button('❌', key=f'cancel_{loan.id}'):
                            cancel_reservation(loan.id)
                            st.rerun()
            
        # Zweiter Teil: Aktive Ausleihen
        with st.container(border=True):
            st.subheader('Aktive Ausleihen')
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            col1.markdown('**Buch**')
            col2.markdown('**Benutzer:in**')
            col3.markdown('**Datum**')
            col4.markdown('**Aktion**')
            st.divider()

            for loan in loans:
                book = get_book_by_id(loan.book_id)
                user = get_user_by_id(loan.user_id)
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

                is_overdue = ((date.today() - loan.due_date).
                                days > 0 if loan.loan_date else False)

                with col1:
                    title = book.title if book else 'Unbekannt'
                    if is_overdue:
                        st.markdown(f'⚠️ {title}')
                    else:
                        st.write(title)
                with col2:
                    st.write(user.name if user else 'Unbekannt')
                with col3:
                    st.write(loan.loan_date.strftime('%d.%m.%Y') 
                            if loan.loan_date else '-')
                with col4:
                    if st.button('📤', key=f'return_{loan.id}'):
                        return_book(loan.id, book.id)
                        st.rerun()
            
            

    st.divider()
    st.caption('⚠️ = Reservierung älter als 7 Tage/ Ausleihe älter als 42 Tage')
    st.caption('✅ = Ausleihe bestätigen')
    st.caption('❌ = Reservierung stornieren')
    st.caption('📤 = Buch zurückgegeben')

# Buch hinzufügen
elif st.session_state.admin_view == 'add_book':
    col1, col2 = st.columns([8, 2])
    with col1:
        st.header('📕+ Neues Buch hinzufügen')
    with col2:
        if st.button('← Zurück'):
            st.session_state.admin_view = 'reservations'
            st.rerun()

    authors = get_all_authors()
    tags = get_all_tags()
    categories = get_all_categories()

    with st.form('add_book_form'):
        title = st.text_input('Titel*')

        selected_author = (st.selectbox('Autor:in auswählen',
                                        ['Autor:in auswählen'] 
                                        + [a.name for a in authors]))
        if selected_author != 'Autor:in auswählen':
            author_id = (next((a.id for a in authors 
                               if a.name == selected_author), None))

        isbn = st.text_input('ISBN*', placeholder='978-3-xxx-xxxxx-x')
        selected_category = (st.selectbox('Kategorie*',
                                          ['Kategorie auswählen'] 
                                          + [c.name for c in categories]))
        category_id = (next((c.id for c in categories 
                             if c.name == selected_category), None))
        selected_tags = st.multiselect('Tags', [t.name for t in tags])
        tag_ids = [t.id for t in tags if t.name in selected_tags]
        publication_year = st.number_input('Jahr', min_value=1000, 
                                           max_value=2100,value=None, 
                                           placeholder='z.B. 2018')
        description = st.text_area('Beschreibung*')

        col_save, col_cancel = st.columns([3, 1])
        with col_save:
            submitted = st.form_submit_button('💾 Buch speichern', 
                                              use_container_width=True)
        with col_cancel:
            cancelled = st.form_submit_button('🚫 Abbrechen', 
                                              use_container_width=True)

    if cancelled:
        st.session_state.admin_view = 'reservations'
        st.rerun()

    if submitted:
        if (not title or not description 
            or selected_category == 'Kategorie auswählen'):
            st.error('Bitte alle Pflichtfelder (*) ausfüllen.')
        else:
            add_book(isbn=isbn, title=title, author_id=author_id,
                     category_id=category_id, tag_ids=tag_ids, 
                     description=description,
                     status='available', publication_year=publication_year,
                     added_date=date.today())

            st.success(f'{title} wurde erfolgreich hinzugefügt!')
            st.session_state.admin_view = 'reservations'
            st.rerun()


# Bücher verwalten
elif st.session_state.admin_view == 'manage_books':
    col1, col2 = st.columns([8, 2])
    with col1:
        st.header('📚 Bücher verwalten')
    with col2:
        if st.button('← Zurück'):
            st.session_state.admin_view = 'reservations'
            st.rerun()

    books = get_all_books()

    search = st.text_input('🔍 Suchen...', placeholder='Titel oder Autor:in')
    if search:
        books = [b for b in books if search.lower() in b.title.lower()
                 or (b.author and search.lower() in b.author.name.lower())]

    st.caption(f'{len(books)} Bücher')
    st.divider()

    for book in books:
        with st.container(border=True):
            col1, col2, col3 = st.columns([6, 1, 1])
            with col1:
                author_name = book.author.name if book.author else 'Unbekannt'
                category_name = book.category.name if book.category else ''
                st.markdown(f'**{book.title}** · {author_name}')
                st.caption(f'{category_name} · {book.status}')
            with col2:
                if st.button('✏️ Bearbeiten', key=f'edit_{book.id}'):
                    st.session_state.editing_book_id = book.id
                    st.session_state.admin_view = 'edit_book'
                    st.rerun()
            with col3:
                if st.button('🗑️ Löschen', key=f'del_{book.id}'):
                    st.session_state[f'confirm_delete_{book.id}'] = True

            # Lösch-Bestätigung
            if st.session_state.get(f'confirm_delete_{book.id}'):
                st.warning(f'Wirklich **{book.title}** löschen?')
                c1, c2 = st.columns(2)
                with c1:
                    if st.button('✅ Ja, löschen', 
                                 key=f'confirm_yes_{book.id}'):
                        delete_book(book.isbn)
                        st.session_state[f'confirm_delete_{book.id}'] = False
                        st.success('Buch gelöscht!')
                        st.rerun()
                with c2:
                    if st.button('❌ Abbrechen', key=f'confirm_no_{book.id}'):
                        st.session_state[f'confirm_delete_{book.id}'] = False
                        st.rerun()


# Buch bearbeiten
elif st.session_state.admin_view == 'edit_book':
    col1, col2 = st.columns([8, 2])
    with col1:
        st.header('✏️ Buch bearbeiten')
    with col2:
        if st.button('← Zurück'):
            st.session_state.admin_view = 'manage_books'
            st.rerun()

    book = get_book_by_id(st.session_state.editing_book_id)
    authors = get_all_authors()
    categories = get_all_categories()
    tags = get_all_tags()

    if not book:
        st.error('Buch nicht gefunden.')
        st.stop()

    current_tag_names = [t.name for t in book.tags]

    with st.form('edit_book_form'):
        title = st.text_input('Titel*', value=book.title)

        author_options = ['(keine)'] + [a.name for a in authors]
        current_author = book.author.name if book.author else '(keine)'
        selected_author = st.selectbox('Autor:in', author_options,
                                        index=(author_options
                                               .index(current_author) 
                                               if current_author 
                                               in author_options else 0))
        author_id = next((a.id for a in authors if a.name == selected_author), 
                         None)

        isbn = st.text_input('ISBN', value=book.isbn or '')

        category_options = ['(keine)'] + [c.name for c in categories]
        current_cat = book.category.name if book.category else '(keine)'
        selected_category = (st.selectbox('Kategorie*', category_options,
                                          index=category_options
                                          .index(current_cat) 
                                          if current_cat 
                                          in category_options 
                                          else 0))
        category_id = (next((c.id for c in categories 
                             if c.name == selected_category), None))

        selected_tags = st.multiselect('Tags', [t.name for t in tags], 
                                       default=current_tag_names)
        tag_ids = [t.id for t in tags if t.name in selected_tags]

        pages = st.number_input('Seiten', value=book.pages)

        publication_year = st.number_input('Jahr', min_value=1000, 
                                           max_value=2100, 
                                           value=book.publication_year or 2000)
        
        description = st.text_area('Beschreibung', 
                                   value=book.description or '')

        status_options = ['available', 'reserved', 'loaned']
        status = st.selectbox('Status', status_options,
                               index=status_options.index(book.status) 
                               if book.status in status_options else 0)

        col_save, col_cancel = st.columns([3, 1])
        with col_save:
            submitted = st.form_submit_button('💾 Änderungen speichern', 
                                              use_container_width=True)
        with col_cancel:
            cancelled = st.form_submit_button('🚫 Abbrechen', 
                                              use_container_width=True)

    if cancelled:
        st.session_state.admin_view = 'manage_books'
        st.rerun()

    if submitted:
        if not title or selected_category == '(keine)':
            st.error('Bitte Titel und Kategorie ausfüllen.')
        else:
            # Buch-Felder aktualisieren
            update_book(id=st.session_state.editing_book_id, 
                            title=title or None,
                            author_id=author_id or None, 
                            isbn=isbn or None,
                            category_id=category_id or None, 
                            tag_ids=tag_ids, 
                            description=description or None,
                            publication_year=publication_year or None, 
                            status=status or None, 
                            added_date=book.added_date or None, 
                            pages=pages or None)

            st.session_state.admin_view = 'manage_books'
            st.rerun()


# Autor:in hinzufügen
elif st.session_state.admin_view == 'manage_author':
    col1, col2 = st.columns([8, 2])
    with col1:
            st.header('✍️+ Neue Autor:in hinzufügen')
    with col2:
        if st.button('← Zurück'):
            st.session_state.admin_view = 'reservations'
            st.rerun()
        
    with st.form('add_author_form'):
        new_author_name = st.text_input('Name der Autor:in*')
        new_author_biography = st.text_input('Biographie*')
        new_author_birth_year = st.text_input('Geburtsjahr*')
        new_author_death_year = st.text_input('Todesjahr')


        col_save, col_cancel = st.columns([3, 1])
        with col_save:
            submitted = st.form_submit_button('💾 Autor:in speichern', 
                                                    use_container_width=True)
        with col_cancel:
            cancelled = st.form_submit_button('🚫 Abbrechen', 
                                                    use_container_width=True)

    if cancelled:
        st.session_state.admin_view = 'reservations'
        st.rerun()

    if submitted:
        if (not new_author_name or not new_author_biography 
            or not new_author_birth_year):
            st.error('Bitte alle Pflichtfelder (*) ausfüllen.')
        else:
            if new_author_name:
                add_author(name=new_author_name, 
                           biography=new_author_biography, 
                           birth_year=new_author_birth_year, 
                           death_year=new_author_death_year)

            st.success(f'{new_author_name} wurde erfolgreich hinzugefügt!')
            st.session_state.admin_view = 'reservations'
            st.rerun()


# User:innen verwalten
elif st.session_state.admin_view == 'manage_users':
    col1, col2 = st.columns([8, 2])
    with col1:
        st.header('👥 User:innen verwalten')
    with col2:
        if st.button('← Zurück'):
            st.session_state.admin_view = 'reservations'
            st.rerun()

    users = get_all_users()


    search = st.text_input('🔍 Suchen...', placeholder='Name oder E-Mail')
    if search:
        users = [u for u in users if search.lower() in u.name.lower()
                 or search.lower() in u.mail.lower()]

    st.caption(f'{len(users)} Benutzer:innen')
    st.divider()

    for user in users:
        with st.container(border=True):
            col1, col2, col3 = st.columns([6, 1, 1])
            with col1:
                admin_badge = '🔑 Admin' if user.is_admin else '👤 User'
                st.markdown(f'**{user.name}** · {user.mail}')
                st.caption(admin_badge)
            with col2:
                if user.id != st.session_state.user.id:
                    if st.button('🔑', key=f'make_admin_{user.id}'):
                        st.session_state[f'confirm_make_admin_{user.id}'] = True
            with col3:
                if user.id != st.session_state.user.id:
                    if st.button('🗑️', key=f'del_user_{user.id}'):
                        st.session_state[f'confirm_del_user_{user.id}'] = True

            if st.session_state.get(f'confirm_del_user_{user.id}'):
                st.warning(f'Wirklich **{user.name}** löschen?')
                c1, c2 = st.columns(2)
                with c1:
                    if st.button('✅ Ja, löschen', 
                                 key=f'confirm_yes_user_{user.id}'):
                        delete_user(user.id)
                        st.session_state[f'confirm_del_user_{user.id}'] = False
                        st.success('User:in gelöscht!')
                        st.rerun()
                with c2:
                    if st.button('❌ Abbrechen', 
                                 key=f'confirm_no_user_{user.id}'):
                        st.session_state[f'confirm_del_user_{user.id}'] = False
                        st.rerun()

            if st.session_state.get(f'confirm_make_admin_{user.id}'):
                st.warning(f'Wirklich **{user.name}** Admin-Rechte vergeben?')
                c1, c2 = st.columns(2)
                with c1:
                    if st.button('✅ Ja', 
                                 key=f'confirm_yes_admin_{user.id}'):
                        update_user(user_id=user.id, is_admin=True)
                        st.session_state[f'confirm_make_admin_{user.id}'] = False
                        st.success('User:in ist jetzt Admin!')
                        st.rerun()
                with c2:
                    if st.button('❌ Abbrechen', 
                                 key=f'confirm_no_admin_{user.id}'):
                        st.session_state[f'confirm_make_admin_{user.id}'] = False
                        st.rerun()
    st.divider()
    st.caption('🔑 = Admin-Rolle zuweisen ')
    st.caption('🗑️ = User:in löschen')

st.caption('* = Pflichtfeld')