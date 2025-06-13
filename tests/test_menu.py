from game.menu import select_map_type
from game.menu import GameMenu
from game.menu import show_intro

def test_select_map_type_returns_map_type(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "2")
    assert select_map_type() == 2

def test_select_map_type_cancel(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "q")
    assert select_map_type() is None


def test_show_intro_runs():
    show_intro()

class DummyGame:
    def __init__(self):
        self.console = None
        self.username = "test_user"
        self.sound = type("DummySound", (), {"set_sfx_volume": lambda s,v: None, "set_music_volume": lambda s,v: None})()

def test_game_menu_init():
    gm = GameMenu(DummyGame())
    assert hasattr(gm, "game")