from typing import List, Tuple, Optional

class Enemy:
    """
    Bazowa klasa wszystkich przeciwników w grze.
    Każdy przeciwnik porusza się po ścieżce na mapie, posiada własne statystyki
    i specjalne cechy.
    """

    def __init__(
        self,
        path: List[Tuple[int, int]],
        name: str,
        hp: int,
        speed: int,
        reward: int,
        symbol: str = "👾",
        spawn_delay: int = 0,
        damage: int = 1
    ) -> None:
        # Parametry bazowe
        self.path = path
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.reward = reward
        self.symbol = symbol
        self.spawn_delay = spawn_delay
        self.damage = damage

        # Stan bieżący
        self.path_index: int = 0
        self.position: Tuple[int, int] = path[0] if path else (0, 0)
        self.alive: bool = True
        self.reached_end: bool = False

        # Efekty statusowe
        self.slowed: int = 0
        self.burning: int = 0
        self.skip_move: bool = False
        self.stunned: int = 0

        # Flagowe cechy specjalne
        self.invisible: bool = False
        self.fire_immune: bool = False
        self.regenerates: bool = False
        self._regen_counter: int = 0
        self.regen_interval: int = 0

    def apply_effects(self) -> None:
        """
        Nakłada efekty statusowe na przeciwnika (np. slow, burn, regen).
        """
        if self.slowed > 0:
            self.slowed -= 1
            self.skip_move = True
        else:
            self.skip_move = False

        if self.burning > 0 and not self.fire_immune:
            self.burning -= 1
            self.take_damage(1)

        if self.regenerates and self._should_regenerate():
            self.hp = min(self.hp + 1, self.max_hp)

    def _should_regenerate(self) -> bool:
        """
        Sprawdza, czy nadszedł moment na regenerację HP.
        """
        self._regen_counter += 1
        if self._regen_counter >= self.regen_interval:
            self._regen_counter = 0
            return True
        return False

    def move(self, all_enemies: Optional[List['Enemy']] = None) -> None:
        """
        Przesuwa przeciwnika po ścieżce (uwzględnia stun, slow, spawn_delay).
        """
        if not self.alive:
            return

        if self.spawn_delay > 0:
            self.spawn_delay -= 1
            return

        if self.stunned > 0:
            self.stunned -= 1
            return

        self.apply_effects()
        if self.skip_move:
            return

        next_index = self.path_index + self.speed
        if next_index >= len(self.path):
            self.alive = False
            self.reached_end = True
            return

        self.path_index = next_index
        self.position = self.path[self.path_index]

    def take_damage(self, amount: int) -> None:
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

class Goblin(Enemy):
    """
    Goblin – podstawowy przeciwnik, niskie HP, niskie obrażenia.
    """
    def __init__(self, path: List[Tuple[int, int]], delay: int = 0) -> None:
        super().__init__(path, name="Goblin", hp=20, speed=1,
                         reward=5, symbol="👺", spawn_delay=delay, damage=1)

class Ork(Enemy):
    """
    Ork – silniejszy przeciwnik, większe obrażenia.
    """
    def __init__(self, path: List[Tuple[int, int]], delay: int = 0) -> None:
        super().__init__(path, name="Ork", hp=25, speed=1,
                         reward=10, symbol="👹", spawn_delay=delay, damage=2)

class Smok(Enemy):
    """
    Smok – boss, dużo HP, duża nagroda, duże obrażenia.
    """
    def __init__(self, path: List[Tuple[int, int]], delay: int = 0) -> None:
        super().__init__(path, name="Smok", hp=100, speed=2,
                         reward=50, symbol="🐉", spawn_delay=delay, damage=5)

class Duch(Enemy):
    """
    Duch – niewidzialny przeciwnik (trudniejszy do trafienia).
    """
    def __init__(self, path: List[Tuple[int, int]], delay: int = 0) -> None:
        super().__init__(path, name="Duch", hp=15, speed=1,
                         reward=12, symbol="👻", spawn_delay=delay, damage=1)
        self.invisible = True

class Nietoperz(Enemy):
    """
    Nietoperz – porusza się po prostej z punktu startowego do bazy (ignoruje ścieżkę mapy).
    """
    def __init__(
        self,
        path: List[Tuple[int, int]],
        delay: int = 0,
        start: Tuple[int, int] = (0, 0),
        target: Tuple[int, int] = (0, 0)
    ) -> None:
        super().__init__(path, name="Nietoperz", hp=5, speed=2,
                         reward=8, symbol="🦇", spawn_delay=delay, damage=1)
        self.position = start
        self.flying = True
        self.target = target

    def move(self, all_enemies: Optional[List['Enemy']] = None) -> None:
        """
        Przemieszcza Nietoperza po linii prostej do bazy (nie po ścieżce).
        """
        if not self.alive:
            return
        if self.spawn_delay > 0:
            self.spawn_delay -= 1
            return
        if self.stunned > 0:
            self.stunned -= 1
            return

        x, y = self.position
        tx, ty = self.target
        dx = (1 if tx > x else -1) if tx != x else 0
        dy = (1 if ty > y else -1) if ty != y else 0
        self.position = (x + dx, y + dy)

        if self.position == self.target:
            self.alive = False
            self.reached_end = True

class Troll(Enemy):
    """
    Troll – przeciwnik regenerujący HP co kilka tur.
    """
    def __init__(self, path: List[Tuple[int, int]], delay: int = 0) -> None:
        super().__init__(path, name="Troll", hp=35, speed=1,
                         reward=15, symbol="🧌", spawn_delay=delay, damage=3)
        self.regenerates = True
        self.regen_interval = 5
        self._regen_counter = 0

class Pajak(Enemy):
    def __init__(self, path: List[Tuple[int, int]], delay: int = 0) -> None:
        super().__init__(path, name="Pająk", hp=10, speed=1,
                         reward=12, symbol="🕷️", spawn_delay=delay, damage=2)

class Rycerz(Enemy):
    """
    Rycerz – odporny na podpalenia.
    """
    def __init__(self, path: List[Tuple[int, int]], delay: int = 0) -> None:
        super().__init__(path, name="Rycerz", hp=18, speed=1,
                         reward=18, symbol="🛡️", spawn_delay=delay, damage=4)
        self.fire_immune = True