from sqlalchemy import (
    create_engine, Column, Integer, String, Text, UniqueConstraint
)
from sqlalchemy.orm import sessionmaker, declarative_base
import datetime
import json
import os

Base = declarative_base()
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "tower_defense.db")
DB_URI = f"sqlite:///{DB_PATH}"

class Highscore(Base):
    __tablename__ = 'highscores'
    username = Column(String, primary_key=True)
    score = Column(Integer, nullable=False)
    date = Column(String, nullable=False)

class Save(Base):
    """
    Zapisane stany gry.
    Kombinacja username, slot jest unikalna.
    """
    __tablename__ = 'saves'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    slot = Column(Integer, nullable=False)
    data = Column(Text, nullable=False)
    __table_args__ = (UniqueConstraint('username', 'slot', name='_username_slot_uc'),)

engine = create_engine(DB_URI, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, future=True)

def init_db():
    """
    Tworzy wszystkie tabele w bazie danych, jeśli jeszcze nie istnieją.
    """
    Base.metadata.create_all(engine)

def add_score(username, score, date=None):
    """
    Dodaje nowy rekord wyniku dla gracza. Jeśli gracz już istnieje, zapisuje tylko wyższy wynik.
    """
    if not date:
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    session = SessionLocal()
    try:
        with session.begin():
            hs = session.query(Highscore).filter_by(username=username).first()
            if hs:
                if score > hs.score:
                    hs.score = score
                    hs.date = date
            else:
                hs = Highscore(username=username, score=score, date=date)
                session.add(hs)
    except Exception as e:
        print(f"❌ Nie udało się dodać wyniku do bazy: {e}")
    finally:
        session.close()

def get_top_scores(limit=10):
    session = SessionLocal()
    try:
        results = (
            session.query(Highscore)
            .order_by(Highscore.score.desc())
            .limit(limit)
            .all()
        )
        return results
    finally:
        session.close()

def delete_score(username):
    """
    Usuwa wynik gracza z rankingu.
    """
    session = SessionLocal()
    try:
        with session.begin():
            hs = session.get(Highscore, username)
            if hs:
                session.delete(hs)
    finally:
        session.close()

def save_game(username, slot, data_json):
    """
    Zapisuje stan gry użytkownika do wybranego slotu.
    """
    session = SessionLocal()
    try:
        with session.begin():
            save = session.query(Save).filter_by(username=username, slot=slot).first()
            if save:
                save.data = data_json
            else:
                save = Save(username=username, slot=slot, data=data_json)
                session.add(save)
    finally:
        session.close()

def load_game(username, slot):
    """
    Wczytuje zapis gry użytkownika z danego slotu.
    """
    session = SessionLocal()
    try:
        save = session.query(Save).filter_by(username=username, slot=slot).first()
        if save:
            try:
                return json.loads(save.data)
            except json.JSONDecodeError:
                print("❌ Zapis gry jest uszkodzony lub nieprawidłowy format.")
                return None
        return None
    except Exception as e:
        print(f"❌ Wystąpił błąd podczas wczytywania gry: {e}")
        return None
    finally:
        session.close()


def delete_save(username, slot):
    """
    Usuwa zapis gry z danego slotu.
    """
    session = SessionLocal()
    try:
        with session.begin():
            save = session.query(Save).filter_by(username=username, slot=slot).first()
            if save:
                session.delete(save)
    finally:
        session.close()

def list_saves_for_user(username):
    """
    Zwraca listę slotów z zapisami gry użytkownika.
    """
    session = SessionLocal()
    try:
        return [f"slot {save.slot}" for save in session.query(Save).filter_by(username=username).all()]
    finally:
        session.close()
    return []