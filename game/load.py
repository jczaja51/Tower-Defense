import json
import logging
from game.map import Map
from game import database
from game.tower import Strzelajaca, CiezkaArmatnia, Lodowa, MagiaOgnia, Laserowa

def load_game(game) -> bool:
    """
    Wczytuje zapis gry danego gracza z bazy.
    """
    try:
        json_data = database.load_game(game.username, game.slot)
        if not json_data:
            return False
        data = json_data if isinstance(json_data, dict) else json.loads(json_data)
    except Exception as e:
        logging.error(f"Błąd wczytywania zapisu z bazy: {e}")
        return False

    _load_game_data(game, data)
    return True

def _load_game_data(game, data: dict):
    """
    Ładuje właściwe dane do obiektu Game — odtwarza stan gry, mapę, wieże, statystyki, osiągnięcia.
    """
    game.difficulty = data.get("difficulty", "Normal")
    game.gold = data["gold"]
    game.lives = data["lives"]
    game.wave_number = data["wave"]
    game.stats = data.get("stats", {}).copy()
    game.hp_scale_per_wave = data.get("hp_scale_per_wave", 1.1)
    game.reward_scale_per_wave = data.get("reward_scale_per_wave", 1.1)

    # Uzupełnianie brakujących statystyk domyślnymi wartościami
    defaults = {
        "zabici_przeciwnicy": 0,
        "wydane_zloto": 0,
        "liczba_ulepszen": 0,
        "towers_built": 0,
        "max_gold_ever": game.gold
    }
    for key, default in defaults.items():
        try:
            game.stats[key] = int(game.stats.get(key, default))
        except (ValueError, TypeError):
            game.stats[key] = default

    # Odtworzenie mapy: układ, ścieżka, start, baza
    m = data["map"]
    game.map_type = m["map_type"]
    game.map = Map(map_type=game.map_type)
    game.map.grid = m["grid"]
    game.map.path = [(int(x), int(y)) for x, y in m["path"]]
    game.map.start = (int(m["start"][0]), int(m["start"][1]))
    game.map.base = (int(m["base"][0]), int(m["base"][1]))

    # Wieże: przywrócenie lokalizacji, typów, poziomów
    game.towers.clear()
    for name, x, y, lvl in data["towers"]:
        cls = {
            "Strzelająca": Strzelajaca,
            "Ciężka Armatnia": CiezkaArmatnia,
            "Lodowa": Lodowa,
            "Magia Ognia": MagiaOgnia,
            "Laserowa": Laserowa
        }[name]
        t = cls(x, y)
        t.game = game
        for _ in range(lvl - 1):
            t.upgrade()
        game.towers.append(t)
        game.map.grid[y][x] = t.symbol

    # Reset stanu dynamicznego: wrogowie, powiadomienia
    game.enemies = []
    game.notifications = []

    # Osiągnięcia ładowane teraz z save'a, a nie z bazy
    game.achievements = data.get("achievements", {
        "sto_pokonanych": False,
        "bogacz": False,
        "architekt": False,
    })

    logging.info(f"Wczytano grę: użytkownik={game.username}, slot={getattr(game, 'slot', '?')}")
    print("✅ Gra wczytana.")