import json
import os
from rich.panel import Panel
from rich.align import Align

PREFS_FILE = "preferences.json"

# Domyślne wartości ustawień rozgrywki dla nowej gry
DEFAULT_PREFS = {
    "mode": "Normal",  # Easy, Normal, Hard, Custom
    "starting_gold": 100,
    "starting_lives": 10,
    "hp_scale_per_wave": 0.10,
    "reward_scale_per_wave": 0.05,
    "num_waves": 20,
    "delay_step": 2,
    "sfx_volume": 0.7,
    "music_volume": 0.4
}

# Presety wybranych poziomów trudności. Każdy preset nadpisuje kluczowe wartości DEFAULT_PREFS.
DIFFICULTY_PRESETS = {
    "Easy": {
        "starting_gold": 140,
        "starting_lives": 25,
        "hp_scale_per_wave": 0.1,
        "reward_scale_per_wave": 0.03,
    },
    "Normal": {
        "starting_gold": 130,
        "starting_lives": 20,
        "hp_scale_per_wave": 0.2,
        "reward_scale_per_wave": 0.05,
    },
    "Hard": {
        "starting_gold": 110,
        "starting_lives": 15,
        "hp_scale_per_wave": 0.3,
        "reward_scale_per_wave": 0.08,
    },
}

def load_prefs():
    """
    Wczytuje preferencje gry z pliku JSON.
    """
    if os.path.exists(PREFS_FILE):
        try:
            with open(PREFS_FILE, "r") as f:
                prefs = json.load(f)
        except json.JSONDecodeError:
            prefs = DEFAULT_PREFS.copy()
    else:
        prefs = DEFAULT_PREFS.copy()
        save_prefs(prefs)
    # Domyślne wartości dla audio, jeśli nie ma ich w pliku
    prefs.setdefault("sfx_volume", 1.0)
    prefs.setdefault("music_volume", 0.5)
    return prefs


def save_prefs(prefs: dict):
    """
    Zapisuje preferencje gry do pliku JSON.
    """
    with open(PREFS_FILE, "w") as f:
        json.dump(prefs, f, indent=2)

def get_int_input(prompt, min_val=None, max_val=None):
    """
    Pobiera liczbę całkowitą od użytkownika z walidacją zakresu.
    """
    while True:
        try:
            value = int(input(prompt))
            if min_val is not None and value < min_val:
                print(f"❌ Wartość musi być większa lub równa {min_val}.")
                continue
            if max_val is not None and value > max_val:
                print(f"❌ Wartość musi być mniejsza lub równa {max_val}.")
                continue
            return value
        except ValueError:
            print("❌ Wpisz poprawną liczbę całkowitą.")

def get_float_input(prompt, min_val=None, max_val=None):
    """
    Pobiera liczbę zmiennoprzecinkową od użytkownika z walidacją zakresu.
    """
    while True:
        try:
            value = float(input(prompt))
            if min_val is not None and value < min_val:
                print(f"❌ Wartość musi być większa lub równa {min_val}.")
                continue
            if max_val is not None and value > max_val:
                print(f"❌ Wartość musi być mniejsza lub równa {max_val}.")
                continue
            return value
        except ValueError:
            print("❌ Wpisz poprawną liczbę (np. 0.1 dla 10%).")

def select_game_mode(console=None):
    """
    Wyświetla menu wyboru trybu gry i zwraca słownik wybranych preferencji.
    Umożliwia wybór jednego z predefiniowanych poziomów trudności lub własnej konfiguracji (Custom).
    """
    if console is None:
        from rich.console import Console
        console = Console()

    while True:
        # Panel wyboru trybu gry
        lines = [
            "[bold cyan]=== WYBÓR TRYBU GRY ===[/bold cyan]\n",
            " [bold]1[/bold] – Easy    🟢",
            " [bold]2[/bold] – Normal  🟡",
            " [bold]3[/bold] – Hard    🔴",
            "[bold]4[/bold] – Custom  🛠️",
            "",
            "Q – ↩️  Cofnij do menu"
        ]
        panel_content = "\n".join(lines)
        panel = Panel(
            Align.center(panel_content, vertical="middle"),
            width=50, padding=(1, 4)
        )
        console.print(panel, justify="center")

        choice = input("Wybierz: ").strip()
        if choice in ('1', '2', '3'):
            mode = {"1": "Easy", "2": "Normal", "3": "Hard"}[choice]
            prefs = DEFAULT_PREFS.copy()
            prefs.update(DIFFICULTY_PRESETS[mode])
            prefs["mode"] = mode
            save_prefs(prefs)
            return prefs
        elif choice == '4':
            # Panel informujący o trybie custom
            custom_panel = Panel(
                Align.center(
                    "[bold magenta]Tryb Custom[/bold magenta]\n"
                    "Wprowadź własne ustawienia gry.",
                    vertical="middle"
                ),
                width=50, padding=(1, 4)
            )
            console.print(custom_panel, justify="center")
            prefs = {}
            prefs["mode"] = "Custom"
            prefs["starting_gold"] = get_int_input("Początkowe złoto: ", min_val=1)
            prefs["starting_lives"] = get_int_input("Początkowe życia: ", min_val=1)
            prefs["hp_scale_per_wave"] = get_float_input("Skalowanie HP co falę (np. 0.1 = +10%): ", min_val=0)
            prefs["reward_scale_per_wave"] = get_float_input("Skalowanie nagród co falę (np. 0.05 = +5%): ", min_val=0)
            prefs["num_waves"] = get_int_input("Liczba fal: ", min_val=1)
            prefs["delay_step"] = get_int_input("Czas opóźnienia między spawnami (s): ", min_val=0)
            save_prefs(prefs)
            return prefs
        elif choice.lower() == 'q':
            return None
        else:
            error_panel = Panel(
                Align.center("❌ Nieprawidłowy wybór. Wybierz 1–4.", vertical="middle"),
                width=50, padding=(1, 4)
            )
            console.print(error_panel, justify="center")