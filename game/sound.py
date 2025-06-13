import threading
import logging
import pygame

from pathlib import Path
from typing import Optional
from game.settings import load_prefs

class SoundManager:
    """
       Zarządza całą obsługą dźwięków gry — efektów SFX i muzyki tła.
       Odpowiada za ładowanie, odtwarzanie, ustawienia głośności i wyciszanie.
       Korzysta z pygame.mixer, obsługuje błędy i preferencje użytkownika.
       """
    SOUND_DIR = Path(__file__).parent.parent / 'sounds'
    # Mapowanie kluczy na pliki dźwiękowe gry
    SFX_MAP = {
        'build':       'build.wav',
        'death':       'enemy_death.wav',
        'lose':        'lose_life.wav',
        'shoot_basic': 'shoot_strzelajaca.wav',
        'shoot_heavy': 'shoot_ciezka.wav',
        'shoot_ice':   'shoot_lodowa.wav',
        'shoot_fire':  'shoot_ognia.wav',
        'shoot_laser': 'shoot_laser.wav',
        'music':       'bgm.wav',
    }

    def __init__(
        self,
        enabled: bool = True,
        debug: bool = False,
        sound_dir: Optional[Path] = None
    ) -> None:
        """
        Inicjalizuje SoundManagera:
            -Ustawia ścieżki do plików dźwięków,
            -Próbuje zainicjować mikser pygame,
            -Ładuje preferencje głośności z bazy,
            -Ładuje muzykę tła.
        """
        self.enabled = enabled
        self.debug = debug
        self._sfx_cache = {}
        self.sfx_volume = 1.0

        if sound_dir:
            self.SOUND_DIR = Path(sound_dir)
        self.music_loaded = False

        try:
            pygame.mixer.init()
        except pygame.error as e:
            logging.error(f"Nie udało się zainicjować miksera dźwięku: {e}")
            self.enabled = False
            return

        # Załaduj preferencje głośności
        prefs = load_prefs()
        self.sfx_volume = float(prefs.get("sfx_volume", 1.0))
        music_volume = float(prefs.get("music_volume", 0.5))

        music_file = self.SFX_MAP.get('music')
        if music_file:
            music_path = self.SOUND_DIR / music_file
            try:
                pygame.mixer.music.load(str(music_path))
                pygame.mixer.music.set_volume(music_volume)
                self.music_loaded = True
                if self.debug:
                    logging.debug(f"Załadowano muzykę: {music_path}")
            except pygame.error as e:
                logging.warning(f"Nie załadowano muzyki tła ({music_path}): {e}")

    def _load_sfx(self, key: str) -> Optional[pygame.mixer.Sound]:
        """
        Ładuje efekt dźwiękowy (SFX) na podstawie klucza, cache'uje obiekt Sound.
        Jeśli plik nie istnieje lub jest błąd, zwraca None.
        """
        if key in self._sfx_cache:
            return self._sfx_cache[key]

        fname = self.SFX_MAP.get(key)
        if not fname:
            return None

        path = self.SOUND_DIR / fname
        try:
            sound = pygame.mixer.Sound(str(path))
            # Ustaw poziom głośności tylko dla efektów
            if key.startswith("shoot_") or key in ("death", "build", "lose"):
                sound.set_volume(self.sfx_volume)
            self._sfx_cache[key] = sound
            return sound
        except pygame.error as e:
            logging.error(f"Błąd ładowania SFX ({path}): {e}")
            return None

    def set_music_volume(self, volume: float) -> None:
        """
        Ustawia głośność muzyki tła (0.0 - 1.0).
        """
        pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
        if self.debug:
            logging.debug(f"Ustawiono głośność muzyki: {volume}")

    def set_sfx_volume(self, volume: float) -> None:
        """
        Ustawia głośność wszystkich efektów SFX (również już załadowanych).
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self._sfx_cache.values():
            sound.set_volume(self.sfx_volume)
        if self.debug:
            logging.debug(f"Ustawiono głośność SFX: {volume}")

    def play(self, key: str, loop: bool = False) -> None:
        """
        Odtwarza efekt SFX lub muzykę tła na podstawie klucza.
        """
        if not self.enabled:
            return

        if key == 'music' and self.music_loaded:
            pygame.mixer.music.play(-1 if loop else 0)
            return

        sfx = self._load_sfx(key)
        if not sfx:
            return

        def _play():
            try:
                sfx.play()
            except pygame.error as e:
                logging.error(f"Błąd odtwarzania SFX: {e}")

        # SFX odtwarzany w osobnym wątku, by nie blokował gry
        threading.Thread(target=_play, daemon=True).start()

    def toggle_mute(self) -> None:
        """
        Pauzuje lub wznawia muzykę tła. Wyciszanie działa tylko na BGM.
        """
        if not self.music_loaded:
            return
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()

    def is_muted(self) -> bool:
        """
        Zwraca True jeśli muzyka tła jest wyciszona (nie gra lub niezaładowana).
        """
        if not self.music_loaded:
            return True
        return not pygame.mixer.music.get_busy()

# Globalna instancja dźwięku dla gry
sound_manager = SoundManager(enabled=True, debug=False)