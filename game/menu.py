import time
import logging
import os
import shutil
from rich.panel import Panel
from rich.align import Align
from game import database
from game.load import load_game
from game.settings import load_prefs, save_prefs, select_game_mode

def show_intro():
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = """
████████╗ ██████╗ ██╗    ██╗███████╗██████╗     ██████╗ ███████╗███████╗███████╗███╗   ██╗███████╗███████╗
╚══██╔══╝██╔═══██╗██║    ██║██╔════╝██╔══██╗    ██╔══██╗██╔════╝██╔════╝██╔════╝████╗  ██║██╔════╝██╔════╝
   ██║   ██║   ██║██║ █╗ ██║█████╗  ██████╔╝    ██║  ██║█████╗  █████╗  █████╗  ██╔██╗ ██║███████╗█████╗  
   ██║   ██║   ██║██║███╗██║██╔══╝  ██╔══██╗    ██║  ██║██╔══╝  ██╔══╝  ██╔══╝  ██║╚██╗██║╚════██║██╔══╝  
   ██║   ╚██████╔╝╚███╔███╔╝███████╗██║  ██║    ██████╔╝███████╗██║     ███████╗██║ ╚████║███████║███████╗
   ╚═╝    ╚═════╝  ╚══╝╚══╝ ╚══════╝╚═╝  ╚═╝    ╚═════╝ ╚══════╝╚═╝     ╚══════╝╚═╝  ╚═══╝╚══════╝╚══════╝
"""
    term_width = shutil.get_terminal_size((80, 20)).columns
    for line in banner.splitlines():
        print(line.center(term_width))

def select_map_type(console=None):
    os.system('cls' if os.name == 'nt' else 'clear')
    if console is None:
        from rich.console import Console
        console = Console()

    while True:
        lines = [
            "[bold cyan]=== WYBÓR MAPY ===[/bold cyan]\n",
            "[bold]1[/bold] – Mapa liniowa (prosta)",
            "[bold]2[/bold] – Mapa losowa (zakręty)",
            "[bold]3[/bold] – Mapa diagonalna (ukośna)",
            "",
            "Q – Cofnij do menu"
        ]
        panel_content = "\n".join(lines)
        panel = Panel(
            Align.center(panel_content, vertical="middle"),
            width=50, padding=(1, 4)
        )
        console.print(panel, justify="center")
        choice = input("Wybierz numer mapy (1–3) lub Q aby wrócić: ").strip().lower()
        if choice == 'q':
            logging.info("[MAP] Gracz anulował wybór mapy (powrót do menu)")
            return None
        if choice in ('1', '2', '3'):
            logging.info(f"[MAP] Gracz wybrał mapę: {choice}")
            return int(choice)
        # Błąd wyboru
        error_panel = Panel(
            Align.center("❌ Nieprawidłowy wybór.", vertical="middle"),
            width=50, padding=(1, 4)
        )
        console.print(error_panel, justify="center")

class GameMenu:
    """
    Klasa GameMenu – interaktywne menu główne gry.

    Obsługuje:
        -wybór i ładowanie zapisów,
        -uruchomienie nowej gry,
        -ustawienia audio,
        -podgląd rankingu,
        -wyjście z gry.
    """
    def __init__(self, game):
        self.game = game
        self.console = game.console

    def show_main_menu(self):
        while True:
            show_intro()
            menu_text = "\n".join([
                f"[bold cyan]Witaj, {self.game.username}![/bold cyan]",
                "",
                "[1] Wczytaj grę",
                "[2] Nowa gra",
                "[S] Ustawienia dźwięku",
                "[R] Ranking",
                "[Q] Wyjdź"
            ])
            panel = Panel(
                Align.center(menu_text, vertical="middle"),
                padding=(1, 4),
                width=60
            )
            self.console.print(panel, justify="center")

            choice = input("\nWybierz opcję: ").strip().lower()
            if choice == '1':
                if self._load_menu():
                    return
            elif choice == '2':
                if self._new_game_flow():
                    return
            elif choice == 's':
                self._sound_settings()
            elif choice == 'r':
                self.game.show_highscores()
                input("\n⏸ Naciśnij Enter, aby wrócić do menu…")
            elif choice == 'q':
                logging.info(f"[MENU] Gracz {self.game.username} zakończył program.")
                exit()
            else:
                print("❌ Nieznana opcja.")
                time.sleep(1)
                logging.warning(f"[MENU] Nieznana opcja: {choice}")

    def _sound_settings(self):
        """
        Panel ustawień głośności efektów dźwiękowych i muzyki.
        Zmiany są zapisywane do preferencji i bazy danych.
        """
        console = self.console
        os.system('cls' if os.name == 'nt' else 'clear')

        while True:
            panel = Panel(
                Align.center(
                    "[bold cyan]=== Ustawienia dźwięku ===[/bold cyan]\n\n"
                    "Podaj głośność efektów (0.0 - 1.0)\n"
                    "Podaj głośność muzyki (0.0 - 1.0)\n",
                    vertical="middle"
                ),
                width=50, padding=(1, 4)
            )
            console.print(panel, justify="center")
            try:
                sfx_input = input("Głośność efektów: ").strip()
                if sfx_input.lower() == "q":
                    os.system('cls' if os.name == 'nt' else 'clear')
                    panel = Panel(
                        Align.center("↩️  Powrót do menu.", vertical="middle"),
                        width=50, padding=(1, 4)
                    )
                    console.print(panel, justify="center")
                    time.sleep(1)
                    return

                music_input = input("Głośność muzyki: ").strip()
                if music_input.lower() == "q":
                    os.system('cls' if os.name == 'nt' else 'clear')
                    panel = Panel(
                        Align.center("↩️  Powrót do menu.", vertical="middle"),
                        width=50, padding=(1, 4)
                    )
                    console.print(panel, justify="center")
                    time.sleep(1)
                    return

                sfx = float(sfx_input)
                music = float(music_input)

                sfx = min(max(sfx, 0.0), 1.0)
                music = min(max(music, 0.0), 1.0)

                self.game.sound.set_sfx_volume(sfx)
                self.game.sound.set_music_volume(music)

                prefs = load_prefs()
                prefs["sfx_volume"] = sfx
                prefs["music_volume"] = music
                save_prefs(prefs)

                # Potwierdzenie
                panel = Panel(
                    Align.center("✅ Zaktualizowano ustawienia dźwięku.", vertical="middle"),
                    width=50, padding=(1, 4)
                )
                console.print(panel, justify="center")
                logging.info(
                    f"[SOUND] Gracz {self.game.username} zaktualizował ustawienia dźwięku: SFX={sfx}, Music={music}")
                time.sleep(2)
                break
            except ValueError:
                # Błędna wartość
                panel = Panel(
                    Align.center("❌ Błędna wartość. Spróbuj ponownie lub wpisz Q aby wrócić.", vertical="middle"),
                    width=50, padding=(1, 4)
                )
                console.print(panel, justify="center")
                logging.warning(f"[SOUND] Gracz {self.game.username} podał błędną wartość głośności.")
                time.sleep(2)

    def _new_game_flow(self):
        """
        Obsługuje proces tworzenia nowej gry:
              -wybór slotu zapisu,
              -wybór mapy,
              -wybór trybu gry,
              -uruchomienie gry.
        """
        console = self.console
        os.system('cls' if os.name == 'nt' else 'clear')
        while True:
            show_intro()
            max_slots = 5
            existing_slots = database.list_saves_for_user(self.game.username)
            taken_slots = set(int(s.split()[-1]) for s in existing_slots if s.split()[-1].isdigit())

            # Informacja o slotach zapisu
            lines = []
            lines.append("[bold cyan]=== SLOTY ZAPISU ===[/bold cyan]\n")
            for slot_num in range(1, max_slots + 1):
                status = "[green]🟩 wolny[/green]" if slot_num not in taken_slots else "[red]🟥 zajęty[/red]"
                lines.append(f"  {slot_num}: {status}")
            lines.append("\n  Q: Cofnij do menu\n")
            slots_panel_content = "\n".join(lines)
            panel = Panel(
                Align.center(slots_panel_content, vertical="middle"),
                width=60, padding=(1, 4)
            )
            console.print(panel, justify="center")

            user_input = input(f"Wybierz numer slotu: ").strip().lower()
            if user_input == "q":
                os.system('cls' if os.name == 'nt' else 'clear')
                panel = Panel(
                    Align.center("↩️  Powrót do menu.", vertical="middle"),
                    width=60, padding=(1, 4)
                )
                console.print(panel, justify="center")
                logging.info(f"[NEW GAME] Gracz: {self.game.username} anulował wybór slotu – powrót do menu.")
                time.sleep(1)
                return False
            try:
                slot = int(user_input)
                if slot < 1 or slot > max_slots:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    panel = Panel(
                        Align.center(f"❌ Wybierz slot z zakresu 1–{max_slots}.", vertical="middle"),
                        width=60, padding=(1, 4)
                    )
                    console.print(panel, justify="center")
                    logging.warning(f"[NEW GAME] Gracz: {self.game.username} podał nieprawidłowy slot: {slot}")
                    time.sleep(1)
                    continue
                if slot in taken_slots:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    panel = Panel(
                        Align.center("❌ Slot już zajęty!", vertical="middle"),
                        width=60, padding=(1, 4)
                    )
                    console.print(panel, justify="center")
                    logging.warning(f"[NEW GAME] Gracz: {self.game.username} próbował wybrać zajęty slot: {slot}")
                    time.sleep(1)
                    continue
                break
            except ValueError:
                os.system('cls' if os.name == 'nt' else 'clear')
                panel = Panel(
                    Align.center("❌ Wpisz poprawny numer lub Q aby wrócić.", vertical="middle"),
                    width=60, padding=(1, 4)
                )
                console.print(panel, justify="center")
                logging.warning(f"[NEW GAME] Gracz: {self.game.username} podał nieprawidłowy numer slotu: {user_input}")
                time.sleep(1)

        # Wybór mapy
        map_type = select_map_type(console)
        if map_type is None:
            os.system('cls' if os.name == 'nt' else 'clear')
            panel = Panel(
                Align.center("↩️  Powrót do menu.", vertical="middle"),
                width=60, padding=(1, 4)
            )
            console.print(panel, justify="center")
            time.sleep(1)
            return False

        # Wybór trybu gry
        os.system('cls' if os.name == 'nt' else 'clear')
        prefs = select_game_mode(console)
        if not prefs:
            os.system('cls' if os.name == 'nt' else 'clear')
            panel = Panel(
                Align.center("↩️  Powrót do menu.", vertical="middle"),
                width=60, padding=(1, 4)
            )
            console.print(panel, justify="center")
            time.sleep(1)
            return False

        self.game.slot = slot
        self.game.map_type = map_type
        logging.info(f"[NEW GAME] Gracz: {self.game.username}, Slot: {slot}, Mapa: {map_type}, Tryb: {prefs['mode']}")

        os.system('cls' if os.name == 'nt' else 'clear')
        self.game.new_game(prefs)

        # Panel startowy z podsumowaniem
        panel = Panel(
            Align.center(
                f"🎲 Rozpoczynasz nową grę!\n\n"
                f"Slot: [bold]{slot}[/bold]\n"
                f"Mapa: [bold]{map_type}[/bold]\n"
                f"Tryb: [bold]{prefs['mode']}[/bold]",
                vertical="middle"
            ),
            title="[bold green]Nowa gra[/bold green]",
            width=60, padding=(1, 4)
        )
        console.print(panel, justify="center")
        time.sleep(3)
        return True

    def _load_menu(self):
        """
        Menu ładowania zapisanych gier:
            -pokazuje dostępne sloty (wszystkie 1-5, z info czy zajęty/wolny)
            -umożliwia wybór ładowania lub usuwania zapisu (tylko na zajętych)
        """
        console = self.console
        os.system('cls' if os.name == 'nt' else 'clear')

        while True:
            show_intro()
            slots = database.list_saves_for_user(self.game.username)
            max_slots = 5

            # Zbierz zajęte sloty (numery)
            taken_slots = []
            for slot_name in slots:
                try:
                    slot_num = int(slot_name.split()[-1])
                    taken_slots.append(slot_num)
                except ValueError:
                    continue

            # Wyświetlanie wszystkich slotów 1-5, z informacją o statusie
            lines = []
            lines.append("[bold cyan]=== Twoje zapisy ===[/bold cyan]\n")
            lines.append(f"{'Slot':<8} {'Status':<8}")
            lines.append("-" * 25)
            for slot_num in range(1, max_slots + 1):
                if slot_num in taken_slots:
                    lines.append(f"Slot {slot_num:<3}  [Zapis]")
                else:
                    lines.append(f"Slot {slot_num:<3}")

            lines.append("\n[L] Wczytaj   [D] Usuń   [Q] Powrót")
            menu_content = "\n".join(lines)

            panel = Panel(
                Align.center(menu_content, vertical="middle"),
                width=60, padding=(1, 4)
            )
            console.print(panel, justify="center")

            # Mapowanie: tylko sloty z zapisem można wybrać do operacji
            slots_map = {str(slot_num): slot_num for slot_num in taken_slots}

            action = input("Wybierz opcję: ").strip().lower()
            if action == 'q':
                os.system('cls' if os.name == 'nt' else 'clear')
                panel = Panel(
                    Align.center("↩️  Powrót do menu.", vertical="middle"),
                    width=60, padding=(1, 4)
                )
                console.print(panel, justify="center")
                logging.info(f"[LOAD MENU] Gracz: {self.game.username} wrócił do menu głównego z menu ładowania.")
                time.sleep(1)
                return False

            if action in ('l', 'd'):
                prompt_text = "Numer slotu do wczytania" if action == 'l' else "Numer slotu do usunięcia"
                while True:
                    panel_prompt = Panel(
                        Align.center(f"{prompt_text} (lub Q aby wrócić):", vertical="middle"),
                        width=60, padding=(1, 4)
                    )
                    console.print(panel_prompt, justify="center")
                    num = input(">>> ").strip().lower()
                    if num == 'q':
                        os.system('cls' if os.name == 'nt' else 'clear')
                        panel = Panel(
                            Align.center("↩️  Powrót do menu.", vertical="middle"),
                            width=60, padding=(1, 4)
                        )
                        console.print(panel, justify="center")
                        logging.info(
                            f"[LOAD MENU] Gracz: {self.game.username} anulował operację {action.upper()} – powrót do menu ładowania.")
                        time.sleep(1)
                        break
                    if num not in slots_map:
                        panel = Panel(
                            Align.center("❌ Nieprawidłowy numer slota (wybierz slot z [Zapis]).", vertical="middle"),
                            width=60, padding=(1, 4)
                        )
                        console.print(panel, justify="center")
                        logging.warning(f"[LOAD MENU] Gracz: {self.game.username} – Nieprawidłowy numer slotu: {num}")
                        continue
                    slot_no = slots_map[num]
                    if action == 'l':
                        os.system('cls' if os.name == 'nt' else 'clear')
                        json_data = database.load_game(self.game.username, slot_no)
                        if not json_data:
                            panel = Panel(
                                Align.center("❌ Nie udało się wczytać zapisu.", vertical="middle"),
                                width=60, padding=(1, 4)
                            )
                            console.print(panel, justify="center")
                            logging.warning(
                                f"[LOAD MENU] Gracz: {self.game.username}, Slot: {slot_no} – Nie udało się wczytać zapisu.")
                            time.sleep(1)
                            return False
                        self.game.slot = slot_no
                        load_game(self.game)
                        logging.info(f"[LOAD MENU] Gracz: {self.game.username}, Slot: {slot_no} – Wczytano zapis.")
                        return True
                    else:  # action == 'd'
                        os.system('cls' if os.name == 'nt' else 'clear')
                        database.delete_save(self.game.username, slot_no)
                        panel = Panel(
                            Align.center(f"🗑️ Usunięto zapis z slotu {slot_no}", vertical="middle"),
                            width=60, padding=(1, 4)
                        )
                        console.print(panel, justify="center")
                        logging.info(f"[LOAD MENU] Gracz: {self.game.username}, Slot: {slot_no} – Usunięto zapis.")
                        time.sleep(1)
                        break

            else:
                os.system('cls' if os.name == 'nt' else 'clear')
                panel = Panel(
                    Align.center("❌ Nieznana opcja. Użyj L, D lub Q.", vertical="middle"),
                    width=60, padding=(1, 4)
                )
                console.print(panel, justify="center")
                logging.warning(f"[LOAD MENU] Gracz: {self.game.username} – Nieznana opcja: {action}")
                time.sleep(1)