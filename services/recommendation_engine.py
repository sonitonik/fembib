from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from database.db import SessionLocal
from models import Loan
from models import Book
from models import Category
from models import Tag
from models import User
from sqlalchemy.orm import joinedload
import numpy as np


# Hilfsfunktion, um aus Kategorie und Tags eines Buchs 
# Feature-Strings zu bauen
def build_features(user_id):
    user_feature = []
    all_feature = []

    session = SessionLocal()
    try:
        loans = (session.query(Loan).filter(Loan.user_id == user_id).
                 filter(Loan.status.in_(['active', 
                                        'reserved', 'returned'])).all())
        all_books = session.query(Book).options(joinedload(Book.category), 
                                                joinedload(Book.tags), 
                                                joinedload(Book.author)).all()
    
        if loans:
            for loan in loans:
                parts= []
                parts.append(loan.book.category.name)
                for tag in loan.book.tags:
                    parts.append(tag.name)
                user_feature.append(' '.join(parts))

        if all_books:
            for book in all_books: 
                parts = []
                parts.append(book.category.name)
                for tag in book.tags: 
                    parts.append(tag.name)
                all_feature.append(' '.join(parts))

        return user_feature, all_feature, all_books
    finally: 
        session.close()


# Speichert die Präferenzen eines Nutzers (Kategorien und Tags)
def save_user_preferences(user_id, category_ids, tag_ids):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id==user_id).first()
        if user:
            user.categories = (session.query(Category).
                               filter(Category.id.in_(category_ids)).all())
            user.tags = (session.query(Tag).
                          filter(Tag.id.in_(tag_ids)).all())
            session.commit()
    finally:
        session.close()

# Empfehlungen für Nutzer:innen mit Historie - 
# basierend auf Ähnlichkeit von Kategorie und Tags
def get_content_based_recommendations(user_id, limit=5):
    user_feature, all_feature, all_books = build_features(user_id)

    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix_all_feature= tfidf_vectorizer.fit_transform(all_feature)
    tfidf_matrix_user_feature= tfidf_vectorizer.transform(user_feature)

    similarity_matrix = cosine_similarity(tfidf_matrix_user_feature, 
                                          tfidf_matrix_all_feature)
    scores = similarity_matrix.sum(axis=0)

    pairs = list(enumerate(scores))
    sorted_pairs = sorted(pairs, key=lambda x: x[1], reverse=True)
    top_pairs = sorted_pairs[:limit]
    recommendations= [all_books[pair[0]] for pair in top_pairs]
    return recommendations


# Empfehlungen basierend auf Präferenzen (für neue Nutzer:innen ohne Historie)
def get_cold_start_recommendations(user_id, limit=5):
    session = SessionLocal()
    try:
        user = (session.query(User)
                .options(joinedload(User.categories), joinedload(User.tags))
                         .filter(User.id == user_id).first())

        if not user.categories and not user.tags:
            return (session.query(Book)
                    .options(joinedload(Book.tags), 
                                               joinedload(Book.author), 
                                               joinedload(Book.category))
                    .filter(Book.status == 'available')
                    .order_by(Book.added_date.desc()).limit(limit)
                    .all())
        
        books = (session.query(Book)
                 .options(joinedload(Book.category), 
                          joinedload(Book.author), 
                          joinedload(Book.tags))
                 .filter(Book.status == 'available')
                 .all())
       
        scored = []
        for book in books:
            score = 0
            for category in user.categories: 
                if book.category.id == category.id: 
                    score +=2
            for tag in user.tags:
                for t in book.tags:
                    if t.id == tag.id:
                            score +=1
            scored.append([book, score])
        
        sorted_pairs = sorted(scored, key=lambda x: x[1], reverse=True)
        top_pairs = sorted_pairs[:limit]
        recommendations = [pair[0] for pair in top_pairs]

        return recommendations
        
    finally: 
        session.close()


# Hauptfunktion für Empfehlungen - entscheidet basierend auf 
# Nutzer:innenhistorie, welche Methode verwendet wird 
def get_recommendations(user_id, limit=5):
    session = SessionLocal()
    try:
        has_loans = session.query(Loan).filter(
            Loan.user_id == user_id,
            Loan.status.in_(['active', 'returned', 'reserved'])
        ).all()
    finally:
        session.close()

    if len(has_loans)>3:
        recommendations = get_content_based_recommendations(user_id, limit)
        if recommendations:
            return recommendations
        
    return get_cold_start_recommendations(user_id, limit)