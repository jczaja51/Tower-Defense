from typing import List, Tuple, Type
import random

from game.enemy import (
    Enemy, Goblin, Ork, Smok, Duch, Nietoperz, Troll, Pajak
)
from game.config import HP_SCALE_PER_WAVE, REWARD_SCALE_PER_WAVE, DELAY_STEP

class Wave:
    """
    Klasa Wave odpowiada za wygenerowanie pojedynczej fali przeciwników.
    Generuje listę wrogów na podstawie numeru fali, ustala parametry (HP, nagroda),
    decyduje o kolejności oraz typach mobów w danej fali.
    """
    BASE_COUNT: int = 5
    GROWTH_PER_WAVE: int = 2

    def __init__(
        self,
        number: int,
        path: List[Tuple[int, int]],
        start_pos: Tuple[int, int],
        base_pos: Tuple[int, int]
    ) -> None:
        """
        Inicjalizuje falę: zapisuje parametry i wywołuje generowanie mobków.
        """
        self.number: int = number
        self.path: List[Tuple[int, int]] = path
        self.start: Tuple[int, int] = start_pos
        self.base: Tuple[int, int] = base_pos
        self.enemies: List[Enemy] = []
        self._generate_enemies()

    def _generate_enemies(self) -> None:
        """
        Tworzy listę przeciwników dla tej fali. Liczba mobków, ich HP i nagrody
        skalują się z numerem fali zgodnie z konfiguracją gry.
        """
        hp_scale = 1 + (self.number - 1) * HP_SCALE_PER_WAVE
        reward_scale = 1 + (self.number - 1) * REWARD_SCALE_PER_WAVE
        total_count = self.BASE_COUNT + (self.number - 1) * self.GROWTH_PER_WAVE

        for idx in range(total_count):
            delay = idx * DELAY_STEP
            EnemyClass = self._select_enemy_class(idx)

            if EnemyClass is Nietoperz:
                # Nietoperz porusza się w linii prostej start->baza (ignoruje ścieżkę)
                enemy = EnemyClass(
                    self.path,
                    delay=delay,
                    start=self.start,
                    target=self.base
                )
            else:
                enemy = EnemyClass(self.path, delay=delay)

            # Skalowanie HP i nagrody
            enemy.max_hp = int(enemy.max_hp * hp_scale)
            enemy.hp = enemy.max_hp
            enemy.reward = int(enemy.reward * reward_scale)

            self.enemies.append(enemy)

    def _select_enemy_class(self, index: int) -> Type[Enemy]:
        """
        Wybiera klasę przeciwnika na danej pozycji w fali.
        Co 10. fala zawsze zaczyna się od bossa (Smok).
        Reszta dobierana jest losowo według dynamicznych wag.

        Args:
            index (int): Indeks mobka w tej fali.

        Returns:
            Type[Enemy]: Klasa przeciwnika do wygenerowania.
        """
        # Co 10 fala pierwszy mob to boss Smok
        if self.number % 10 == 0 and index == 0:
            return Smok

        weights: dict = {
            Goblin:    max(0.4, 0.8  - self.number * 0.02),        # Goblin dominuje na starcie, później rzadziej
            Ork:       min(0.3, 0.1  + self.number * 0.01),        # Ork coraz częstszy
            Troll:     min(0.15, 0.05 + self.number * 0.005),      # Troll pojawia się częściej z czasem
            Pajak:     0.10,                                       # Stała szansa na Pająka
            Duch:      0.05,                                       # Duch – rzadko
            Nietoperz: 0.05                                        # Nietoperz – rzadko
        }
        total_w = sum(weights.values())
        choices = list(weights.keys())
        probabilities = [w / total_w for w in weights.values()]

        return random.choices(choices, probabilities, k=1)[0]