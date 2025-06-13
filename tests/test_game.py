from unittest.mock import patch, MagicMock

@patch("game.game.GameMenu")
@patch("game.game.database.init_db")
@patch("game.game.sound_manager")
@patch("game.game.load_prefs")
def test_game_init(mock_load_prefs, mock_sound, mock_init_db, mock_gamemenu):
    mock_load_prefs.return_value = {
        "mode": "Normal",
        "sfx_volume": 0.5,
        "music_volume": 0.5,
        "starting_gold": 150,
        "starting_lives": 12,
        "num_waves": 5,
        "hp_scale_per_wave": 1.2,
        "reward_scale_per_wave": 0.7,
    }
    mock_sound.play = MagicMock()

    game = __import__("game.game", fromlist=["Game"]).Game(username="TestUser")

    assert game.username == "TestUser"
    assert game.gold == 150
    assert game.lives == 12
    assert game.num_waves == 5
    assert game.difficulty == "Normal"
    assert isinstance(game.stats, dict)
    assert game.stats["max_gold_ever"] == 150

    game.map = MagicMock()
    game.map.WIDTH = 26
    game.map.HEIGHT = 26
    assert game.parse_coordinates("A1") == (0, 0)
    assert game.parse_coordinates("Z26") == (25, 25)
    assert game.parse_coordinates("AA1") == (None, None)

    with patch("game.game.Panel"), patch.object(game.console, "print"):
        game.show_achievements()

    game.stats["zabici_przeciwnicy"] = 200
    game.stats["max_gold_ever"] = 2000
    game.stats["towers_built"] = 30
    game.update_achievements()
    assert all(game.achievements.values())