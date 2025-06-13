"""
Uruchamia grę Tower Defense w trybie terminalowym:
    -obsługuje argumenty uruchomieniowe (tryb, nick, wyciszenie),
    -inicjalizuje bazę danych,
    -tworzy główny obiekt gry oraz interfejs UI (Rich).

Możliwości CLI:
    --mute – wyciszenie dźwięków
    --nick <nazwa> – nick gracza

Po uruchomieniu skryptu program przechodzi do głównej pętli gry.
"""

from game.game import Game
from ui.game_ui import GameUI
import argparse
from game import database
import logging

# Ustawienia logowania – wszystkie zdarzenia są zapisywane do pliku tower_defense.log
logging.basicConfig(
    filename="tower_defense.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def parse_args():
    """
    Parsuje argumenty wiersza poleceń:
        --mute   – wyciszenie dźwięków
        --nick   – nick gracza
    """
    parser = argparse.ArgumentParser(description="Tower Defense - gra tekstowa")
    parser.add_argument('--mute', action='store_true', help='Wycisza dźwięki gry')
    parser.add_argument('--nick', type=str, help='Nick gracza')
    return parser.parse_args()

if __name__ == '__main__':
    # Inicjalizacja bazy danych, uruchomienie gry z argumentami CLI
    database.init_db()
    args = parse_args()

    g = Game(
        username=args.nick,
        sound_enabled=not args.mute
    )

    ui = GameUI(g)
    ui.run()