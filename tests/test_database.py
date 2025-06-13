import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from game import database

@pytest.fixture(scope="function")
def in_memory_db(monkeypatch):
    engine = create_engine("sqlite:///:memory:", future=True)
    database.Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, future=True)
    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(database, "SessionLocal", session)
    return session

def test_add_and_get_score(in_memory_db):
    scores = database.get_top_scores()
    assert scores == []

    database.add_score("kuba", 123)
    scores = database.get_top_scores()
    assert len(scores) == 1
    assert scores[0].username == "kuba"
    assert scores[0].score == 123

def test_save_and_load_game(in_memory_db):
    data = {"test": 42}
    database.save_game("tester", 1, '{"test": 42}')
    loaded = database.load_game("tester", 1)
    assert loaded == data