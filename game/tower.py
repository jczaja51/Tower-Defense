from abc import ABC, abstractmethod
from game.utils import manhattan_distance
from game.sound import sound_manager
import random

class Tower(ABC):
    """
    Bazowa klasa wieży – logika zasięgu, ataku, ulepszania i statystyk.
    Wszystkie specjalistyczne wieże dziedziczą z niej podstawowe funkcjonalności.
    """
    MAX_LEVEL = 20
    COST_GROWTH = 1.25

    def __init__(self, x, y, name, range_, damage, rate, cost):
        self.x = x
        self.y = y
        self.name = name
        self.range = range_
        self.damage = damage
        self.rate = rate
        self.base_cost = cost
        self.cost = cost

        self.cooldown = 0
        self.level = 1
        self.symbol = "?"
        self.hits = 0
        self.total_damage = 0
        self.can_hit_invisible = False
        self.game = None

    @classmethod
    def max_level(cls):
        """
        Zwraca maksymalny poziom dla tej klasy wieży.
        """
        return cls.MAX_LEVEL

    @property
    def attack_speed(self) -> float:
        try:
            return round(1 / self.rate, 2)
        except ZeroDivisionError:
            return 0.0

    def in_range(self, enemy) -> bool:
        row, col = enemy.position
        return manhattan_distance(self.x, self.y, col, row) <= self.range

    def iter_targets(self, enemies):
        for e in enemies:
            if (
                e.alive and
                (not getattr(e, 'invisible', False) or self.can_hit_invisible) and
                self.in_range(e)
            ):
                yield e

    def find_targets(self, enemies):
        return list(self.iter_targets(enemies))

    @abstractmethod
    def shoot(self, enemy):
        """
        Abstrakcyjna metoda strzału. Każda wieża musi mieć własną implementację.
        """
        pass

    def attack(self, enemies):
        """
        Atakuje najsłabszego przeciwnika w zasięgu (jeśli cooldown = 0).
        """
        if self.cooldown > 0:
            self.cooldown -= 1
            return

        targets = list(self.iter_targets(enemies))
        if not targets:
            return

        target = min(targets, key=lambda e: e.hp)
        self.shoot(target)
        self.cooldown = self.rate

    def upgrade_cost(self) -> int:
        return int(self.base_cost * (self.COST_GROWTH ** (self.level - 1)))

    def can_upgrade(self) -> bool:
        return self.level < self.max_level()

    def upgrade(self) -> bool:
        if not self.can_upgrade():
            return False
        self.range += 1
        self.damage += 1
        self.level += 1
        self.rate = max(1, self.rate - 1)
        self.cost = self.upgrade_cost()
        return True

    def stats(self) -> dict:
        return {
            "Typ": self.name,
            "Poziom": self.level,
            "Zasięg": self.range,
            "Obrażenia": self.damage,
            "Tur/cooldown": self.rate,
            "Atak/s": self.attack_speed,
            "Trafienia": self.hits,
            "Łączny dmg": self.total_damage,
            "Następny lvl (koszt)": self.upgrade_cost() if self.can_upgrade() else "—"
        }

class Strzelajaca(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, "Strzelająca", 3, 2, 1, 50)
        self.symbol = "▲"
        self.tower_type = "basic"
        self.shot_counter = 0

    def shoot(self, enemy):
        self.shot_counter += 1
        dmg = self.damage
        if self.shot_counter % 5 == 0:
            dmg *= 2
        try:
            enemy.take_damage(dmg)
        except Exception as e:
            raise RuntimeError(f"Nie udało się zadać obrażeń: {e}")
        self.hits += 1
        self.total_damage += dmg
        sound_manager.play("shoot_basic")

class CiezkaArmatnia(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, "Ciężka Armatnia", 2, 5, 2, 120)
        self.symbol = "☢"
        self.tower_type = "heavy"

    def shoot(self, enemy):
        try:
            enemy.take_damage(self.damage)
            if random.random() < 0.3:
                enemy.stunned = 1
        except Exception as e:
            raise RuntimeError(f"Nie udało się zadać obrażeń: {e}")
        self.hits += 1
        self.total_damage += self.damage
        sound_manager.play("shoot_heavy")

class Lodowa(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, "Lodowa", 3, 2, 1, 70)
        self.symbol = "❄"
        self.tower_type = "ice"

    def shoot(self, enemy):
        try:
            enemy.take_damage(self.damage)
            enemy.slowed = 2
        except Exception as e:
            raise RuntimeError(f"Nie udało się zadać obrażeń: {e}")
        self.hits += 1
        self.total_damage += self.damage
        sound_manager.play("shoot_ice")

    def attack(self, enemies):
        if self.cooldown > 0:
            self.cooldown -= 1
            return

        alive = [e for e in enemies if e.alive]
        alive.sort(key=lambda e: e.path_index, reverse=True)
        for e in alive:
            if self.in_range(e):
                self.shoot(e)
                self.cooldown = self.rate
                return

class MagiaOgnia(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, "Magia Ognia", 3, 2, 2, 100)
        self.symbol = "*"
        self.can_hit_invisible = True
        self.tower_type = "fire"

    def shoot(self, enemy):
        try:
            enemy.take_damage(self.damage, damage_type="fire")
            enemy.burning = 3
        except Exception as e:
            raise RuntimeError(f"Nie udało się zadać obrażeń: {e}")
        self.hits += 1
        self.total_damage += self.damage
        sound_manager.play("shoot_fire")

    def attack(self, enemies):
        if self.cooldown > 0:
            self.cooldown -= 1
            return

        alive_sorted = sorted(
            filter(lambda opponent: opponent.alive, enemies),
            key=lambda opponent: opponent.path_index,
            reverse=True
        )
        for enemy in alive_sorted:
            if self.in_range(enemy):
                self.shoot(enemy)
                self.cooldown = self.rate
                return

class Laserowa(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, "Laserowa", 4, 2, 1, 60)
        self.symbol = "✦"
        self.can_hit_invisible = True
        self.tower_type = "laser"

    def shoot(self, enemy):
        try:
            enemy.take_damage(self.damage)
            enemy.marked_for_gold = True
        except Exception as e:
            raise RuntimeError(f"Nie udało się zadać obrażeń: {e}")
        self.hits += 1
        self.total_damage += self.damage
        sound_manager.play("shoot_laser")

    def attack(self, enemies):
        if self.cooldown > 0:
            self.cooldown -= 1
            return

        hits = 0
        max_hits = 5
        for e in self.iter_targets(enemies):
            self.shoot(e)
            hits += 1
            if hits >= max_hits:
                break

        self.cooldown = self.rate