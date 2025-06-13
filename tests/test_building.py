import pytest
from unittest.mock import patch, MagicMock
from game.building import Building

@pytest.fixture
def fake_game():
    game = MagicMock()
    game.gold = 100
    game.notifications = []
    game.towers = []
    game.stats = {"wydane_zloto": 0, "towers_built": 0, "max_gold_ever": 0, "zabici_przeciwnicy": 0}
    game.username = "Tester"
    game.sound.play = MagicMock()
    game.save_game = MagicMock()
    class DummyMap:
        path = set()
        start = (0, 0)
        base = (5, 5)
        grid = [[None]*10 for _ in range(10)]
    game.map = DummyMap()
    game.parse_coordinates = MagicMock(return_value=(1, 3))
    return game

@patch('builtins.input', side_effect=['1', 'B4'])
def test_build_tower_with_mocked_input_and_sound(_, fake_game):
    b = Building(fake_game)
    b.build_tower()
    fake_game.sound.play.assert_called_with("build")
    assert len(fake_game.towers) == 1