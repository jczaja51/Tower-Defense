from game.settings import load_prefs

# Podstawowe wymiary planszy gry
MAP_WIDTH  = 26
MAP_HEIGHT = 26

# Wczytanie spersonalizowanych preferencji gracza z pliku konfiguracyjnego
_prefs = load_prefs()

# Kluczowe parametry startowe gry, możliwe do dostosowania przez gracza w ustawieniach
START_GOLD            = _prefs.get("starting_gold", 100)          # Ilość złota na start
START_LIVES           = _prefs.get("starting_lives", 10)          # Liczba żyć na start
NUM_WAVES             = _prefs.get("num_waves", 20)               # Liczba fal w jednej rozgrywce
DELAY_STEP            = _prefs.get("delay_step", 2)               # Odstęp czasowy (np. między falami)
HP_SCALE_PER_WAVE     = _prefs.get("hp_scale_per_wave", 0.10)     # Przyrost HP przeciwników z każdą falą (%)
REWARD_SCALE_PER_WAVE = _prefs.get("reward_scale_per_wave", 0.05) # Przyrost nagród za przeciwników z każdą falą (%)