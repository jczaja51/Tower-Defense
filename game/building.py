import logging
from game.tower import Strzelajaca, CiezkaArmatnia, Lodowa, MagiaOgnia, Laserowa

class Building:
    """
    Klasa odpowiadająca za budowanie i ulepszanie wież.
    Pozwala graczowi postawić nową wieżę lub ulepszyć istniejącą, aktualizuje mapę, stan gry oraz osiągnięcia.
    """
    def __init__(self, game):
        self._game = game

    def build_tower(self):
        print("\nDostępne wieże do budowy:")
        print("Nr | Typ               | Koszt | Zasięg | Obrażenia | Atak/s | Efekt specjalny")
        print("---+-------------------+-------+--------+-----------+--------+-----------------")
        stats = [
            (1, "Strzelająca", 50, 3, 2, 1.0, "–"),
            (2, "Ciężka Armatnia", 110, 2, 5, 0.5, "–"),
            (3, "Lodowa", 70, 2, 1, 1.0, "spowalnia"),
            (4, "Magia Ognia", 100, 3, 1, 0.8, "podpala"),
            (5, "Laserowa", 60, 4, 1, 2.0, "przebija")
        ]
        list(map(lambda t: print(f"{t[0]:2} | {t[1]:<17} | {t[2]:5} | {t[3]:6} | {t[4]:^9} | {t[5]:^6.1f} | {t[6]}"),
                 stats))

        choice = input("\nWybierz numer wieży (Q=Anuluj): ").strip().lower()
        if choice == 'q':
            self._game.notifications.append("Anulowano budowę.")
            return
        if not choice.isdigit() or int(choice) not in range(1, 6):
            self._game.notifications.append("❌ Nieprawidłowy numer wieży.")
            return

        cls_map = {
            1: Strzelajaca,
            2: CiezkaArmatnia,
            3: Lodowa,
            4: MagiaOgnia,
            5: Laserowa
        }
        tower = cls_map[int(choice)](0, 0)
        tower.game = self._game

        coord = input("Podaj współrzędne (np. B4) lub Q=Anuluj: ").strip().upper()
        if coord.lower() == 'q':
            self._game.notifications.append("Anulowano budowę.")
            return

        x, y = self._game.parse_coordinates(coord)
        # Walidacja współrzędnych i pola na mapie
        if x is None:
            self._game.notifications.append("❌ Nieprawidłowe pole.")
            return
        if (y, x) in self._game.map.path or (y, x) == self._game.map.start or (y, x) == self._game.map.base:
            self._game.notifications.append("❌ Nie można na ścieżce, starcie ani bazie.")
            return
        if self._game.gold < tower.cost:
            self._game.notifications.append("❌ Brak złota.")
            return

        # Umieszczanie wieży i aktualizacja gry
        tower.x, tower.y = x, y
        self._game.towers.append(tower)
        self._game.map.grid[y][x] = tower.symbol
        self._game.gold -= tower.cost
        self._game.stats["wydane_zloto"] += tower.cost
        self._game.stats["towers_built"] += 1
        self._game.stats["max_gold_ever"] = max(self._game.stats["max_gold_ever"], self._game.gold)

        self._game.update_achievements()
        logging.info(f"Gracz {self._game.username} postawił {tower.name} na {coord}")
        self._game.notifications.append(f"✅ Postawiono {tower.name} na {coord}.")
        self._game.sound.play("build")
        self._game.save_game()

    def upgrade_tower(self):
        if not self._game.towers:
            self._game.notifications.append("❌ Brak wież do ulepszenia.")
            return

        print("\nIstniejące wieże:")
        print("Nr | Typ               | Poziom | MaxLvl | Pozycja | Obecne dmg | Nowe dmg | Koszt ulepszenia")
        print("---+-------------------+--------+--------+---------+------------+----------+-----------------")

        tower_info = [
            f"{nr:2} | {t.name:<17} | {t.level:^6} | {t.__class__.max_level():^6} | {chr(65 + t.x)}{t.y + 1:^7} | "
            f"{t.damage:^10} | {int(t.damage * 1.2):^8} | {int(t.cost * 0.75):^15}"
            for nr, t in enumerate(self._game.towers, 1)
        ]
        print('\n'.join(tower_info))

        choice = input("\nWybierz numer (Q=Anuluj): ").strip().lower()
        if choice == 'q':
            self._game.notifications.append("Anulowano ulepszenie.")
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(self._game.towers)):
            self._game.notifications.append("❌ Nieprawidłowy numer.")
            return

        tower = self._game.towers[int(choice) - 1]
        if tower.level >= tower.__class__.max_level():
            self._game.notifications.append(
                f"❌ {tower.name} osiągnęła maksymalny poziom ({tower.level}/{tower.__class__.max_level()})."
            )
            return

        cost = int(tower.cost * 0.75)

        confirm = input(f"Ulepszyć {tower.name} za {cost} zł? (T/N): ").strip().lower()
        if confirm != 't':
            self._game.notifications.append("Anulowano ulepszenie.")
            return
        if self._game.gold < cost:
            self._game.notifications.append("❌ Brak złota.")
            return

        self._game.gold -= cost
        self._game.stats["wydane_zloto"] += cost
        self._game.stats["liczba_ulepszen"] += 1
        tower.upgrade()

        logging.info(
            f"Gracz {self._game.username} ulepszył {tower.name} na {tower.x},{tower.y} do poziomu {tower.level}"
        )
        self._game.notifications.append(f"✅ Ulepszono {tower.name} do poziomu {tower.level}.")
        self._game.save_game()