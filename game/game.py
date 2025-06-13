import os
import sys
import json
import logging
import re

from game.building import Building
from game.wave_loop import WaveLoop
from game import database
from game.map import Map
from game.sound import sound_manager
from game.settings import load_prefs
from typing import Tuple, Optional
from game.ranking import Ranking
from game.menu import GameMenu

from rich.console import Console
from rich.panel import Panel

class Game(WaveLoop, Building, Ranking):
    """
    Główna klasa gry.
    Łączy logikę planszy, sterowania, rankingów, budowania, fal i systemu dźwięku.
    Obsługuje pełen cykl gry: inicjalizację, zapisy, osiągnięcia i menu.
    """

    def __init__(self, username=None, difficulty=None, sound_enabled=True):
        # Wywołanie konstruktorów klas bazowych (z przekazaniem self)
        WaveLoop.__init__(self, self)
        Building.__init__(self, self)
        Ranking.__init__(self, self)

        # Inicjalizacja wszystkich atrybutów instancyjnych
        self.map = None
        self.map_type = None
        self.difficulty = None
        self.gold = 0
        self.lives = 0
        self.num_waves = 0
        self.hp_scale_per_wave = 1
        self.reward_scale_per_wave = 1
        self.wave_number = 0
        self.enemies = []
        self.towers = []
        self.game_speed = 1.0
        self.stats = {}
        self.achievements = {}
        self.notifications = []
        self.save_file = None
        self.slot = None

        # Załaduj preferencje
        prefs = load_prefs()
        logging.debug("Załadowano preferencje gry.")
        self.difficulty = difficulty or prefs.get("mode", "Normal")

        # Inicjalizacja dźwięku
        self.sound = sound_manager
        self.sound.enabled = sound_enabled
        self.sound.sfx_volume = prefs.get("sfx_volume", 0.5)
        self.sound.music_volume = prefs.get("music_volume", 0.5)
        self.sound.play("music", loop=True)
        logging.debug(f"Dźwięk uruchomiony: enabled={sound_enabled}")

        # Zasoby startowe
        self.gold = prefs["starting_gold"]
        self.lives = prefs["starting_lives"]
        self.num_waves = prefs["num_waves"]
        self.hp_scale_per_wave = prefs["hp_scale_per_wave"]
        self.reward_scale_per_wave = prefs["reward_scale_per_wave"]

        self.console = Console()
        os.system('cls' if os.name == 'nt' else 'clear')

        # Ustawianie nicku gracza
        if username and re.fullmatch(r"\w{3,15}", username):
            self.username = username
            database.init_db()
        else:
            while True:
                nick = self.console.input("Podaj swój nick (3–15 znaków): ").strip()
                if re.fullmatch(r"\w{3,15}", nick):
                    self.username = nick
                    database.init_db()
                    break
                else:
                    print("❌ Nieprawidłowy nick. Użyj 3–15 znaków (litery, cyfry, podkreślenie).")

        # Statystyki początkowe
        self.stats = {
            "zabici_przeciwnicy": 0,
            "wydane_zloto": 0,
            "liczba_ulepszen": 0,
            "towers_built": 0,
            "max_gold_ever": self.gold
        }
        logging.debug(f"Ustawiono statystyki początkowe: {self.stats}")

        # Osiągnięcia — domyślne
        self.achievements = {
            "sto_pokonanych": False,
            "bogacz": False,
            "architekt": False
        }

        # Kompozycja funkcjonalności
        self.building = Building(self)
        self.wave_loop = WaveLoop(self)
        self.ranking = Ranking(self)

        # Menu główne gry
        GameMenu(self).show_main_menu()

    def delete_save(self, filename):
        """
        Usuwa plik zapisu gry oraz powiązany wynik w rankingu.
        Kończy program, jeśli usuwany jest aktywny zapis.
        """
        try:
            os.remove(filename)
            logging.info(f"Usunięto plik save: {filename}")
        except OSError as e:
            logging.warning(f"Nie udało się usunąć {filename}: {e}")
            print(f"❌ Nie udało się usunąć {filename}: {e}")
            return

        try:
            database.delete_score(self.username)
            logging.info(f"Usunięto wynik z rankingu: {self.username}")
        except Exception as e:
            logging.error(f"Błąd podczas usuwania z rankingu: {e}")
            print(f"❌ Błąd podczas usuwania z rankingu: {e}")

        input("⏸ Naciśnij Enter, aby wrócić do menu…")
        if filename == self.save_file:
            logging.warning(f"Usunięto aktywny zapis, gra zostanie zakończona")
            print("Usunięto aktywny zapis — zamykam grę.")
            sys.exit(0)

    def list_saves(self):
        """
        Zwraca listę nazw plików zapisów dla zalogowanego użytkownika.
        """
        slots = database.list_saves_for_user(self.username)
        return [f"save_{self.username}_slot{s}.json" for s in slots]

    def new_game(self, prefs):
        """
        Resetuje parametry gry i rozpoczyna nową rozgrywkę z ustalonymi preferencjami.
        Tworzy nową mapę, zeruje fale, złoto, statystyki i powiadomienia.
        """
        self.difficulty = prefs["mode"]
        self.map = Map(map_type=self.map_type)
        self.towers.clear()
        self.gold = prefs["starting_gold"]
        self.lives = prefs["starting_lives"]
        self.num_waves = prefs["num_waves"]
        self.hp_scale_per_wave = prefs["hp_scale_per_wave"]
        self.reward_scale_per_wave = prefs["reward_scale_per_wave"]
        self.wave_number = 0
        self.enemies.clear()
        self.game_speed = 1.0
        self.stats = {
            "zabici_przeciwnicy": 0,
            "wydane_zloto": 0,
            "liczba_ulepszen": 0,
            "towers_built": 0,
            "max_gold_ever": prefs["starting_gold"]
        }
        self.notifications.clear()
        # Reset osiągnięć na nową grę
        self.achievements = {
            "sto_pokonanych": False,
            "bogacz": False,
            "architekt": False
        }
        self.save_game()
        logging.info(
            f"Nowa gra utworzona dla gracza {self.username}, tryb: {self.difficulty}, mapa: {self.map_type}, slot: {self.slot}"
        )

    def save_game(self):
        """
        Zapisuje stan gry do bazy w aktualnym slocie.
        Serializuje całą logikę: mapę, wieże, statystyki, poziom fali itd.
        """
        data = {
            "username": self.username,
            "difficulty": self.difficulty,
            "gold": self.gold,
            "lives": self.lives,
            "wave": self.wave_number,
            "stats": self.stats,
            "hp_scale_per_wave": self.hp_scale_per_wave,
            "reward_scale_per_wave": self.reward_scale_per_wave,
            "map": {
                "map_type": self.map_type,
                "grid": self.map.grid,
                "path": [list(p) for p in self.map.path],
                "start": list(self.map.start),
                "base": list(self.map.base),
            },
            "towers": [(t.name, t.x, t.y, t.level) for t in self.towers],
            "achievements": self.achievements.copy(),
        }
        json_data = json.dumps(data)
        if self.slot is None:
            self.slot = 1
        database.save_game(self.username, self.slot, json_data)
        logging.info(f"Zapisano grę: użytkownik={self.username}, slot={self.slot}")
        print("💾 Gra zapisana do bazy danych.")

    def parse_coordinates(self, s: str) -> Tuple[Optional[int], Optional[int]]:
        """
        Parsuje współrzędne planszy w formacie np. 'A5' na indeksy (x, y).
        """
        if not re.fullmatch(r"[A-Z]\d{1,2}", s.upper()):
            return None, None
        try:
            col = ord(s[0].upper()) - ord('A')
            row = int(s[1:]) - 1
            if 0 <= col < self.map.WIDTH and 0 <= row < self.map.HEIGHT:
                logging.debug(f"Parsowanie koordynatów z wejścia: {s} → ({col}, {row})")
                return col, row
        except (IndexError, ValueError, TypeError):
            pass
        return None, None

    def show_achievements(self):
        """
        Wyświetla panel osiągnięć gracza oraz postęp do kolejnych odblokowań.
        """
        self.stats["max_gold_ever"] = max(self.stats.get("max_gold_ever", 0), self.gold)
        updated_achievements = {
            "sto_pokonanych": self.stats.get("zabici_przeciwnicy", 0) >= 100,
            "bogacz": self.stats.get("max_gold_ever", 0) >= 1000,
            "architekt": self.stats.get("towers_built", 0) >= 20,
        }
        logging.debug(f"Osiągnięcia gracza {self.username}: {updated_achievements}")

        lines = [
            f"[{'✅' if updated_achievements['sto_pokonanych'] else '🔒'}] 100 pokonanych przeciwników ({self.stats.get('zabici_przeciwnicy', 0)}/100)",
            f"[{'✅' if updated_achievements['bogacz'] else '🔒'}] 1000 zł w banku ({self.stats.get('max_gold_ever', 0)}/1000)",
            f"[{'✅' if updated_achievements['architekt'] else '🔒'}] 20 wież zbudowanych ({self.stats.get('towers_built', 0)}/20)",
        ]
        panel = Panel("\n".join(lines), title="🏅 Twoje osiągnięcia i postępy")
        self.console.print(panel)

    def update_achievements(self):
        unlocked = {
            "sto_pokonanych": self.stats.get("zabici_przeciwnicy", 0) >= 100,
            "bogacz": self.stats.get("max_gold_ever", 0) >= 1000,
            "architekt": self.stats.get("towers_built", 0) >= 20,
        }
        if unlocked != self.achievements:
            logging.info(f"Zaktualizowano osiągnięcia gracza {self.username}: {unlocked}")
            self.achievements = unlocked.copy()