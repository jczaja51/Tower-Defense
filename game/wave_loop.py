import time
from rich.live import Live
from game.wave import Wave

class WaveLoop:
    """
    Klasa WaveLoop zarządza całą logiką pojedynczej fali.
    """

    def __init__(self, game):
        self.game = game

    def process_enemy_base_entry(self, enemy):
        """Obsługa sytuacji, gdy wróg dotarł do bazy."""
        enemy.reached_end = True
        enemy.alive = False
        self.game.lives -= enemy.damage
        self.game.notifications.append(f"⚠️ {enemy.name} dotarł do bazy! -{enemy.damage} ❤️")
        self.game.sound.play("lose")
        time.sleep(0.1)

    def process_enemy_reward(self, enemy):
        """Obsługa przyznania nagrody za pokonanego wroga."""
        reward = int(enemy.reward * (1.5 if getattr(enemy, 'marked_for_gold', False) else 1))
        self.game.gold += reward
        enemy.rewarded = True
        self.game.stats["zabici_przeciwnicy"] += 1
        self.game.update_achievements()
        self.game.notifications.append(f"💥 Pokonano {enemy.name}! +{reward} złota")
        self.game.sound.play("death")
        time.sleep(0.1)

    def start_wave(self, ui):
        self.game.wave_number += 1
        wave = Wave(
            self.game.wave_number,
            self.game.map.path,
            self.game.map.start,
            self.game.map.base
        )
        self.game.enemies = wave.enemies

        self.game.notifications.append(f"🌊 Rozpoczyna się fala {self.game.wave_number}!")
        ui.simple_animated_event(
            f"ROZPOCZYNA SIĘ FALA {self.game.wave_number}!",
            emoji="🌊",
            color="bold blue",
            hold_time=1.5
        )

        with Live(ui.layout, refresh_per_second=10, console=ui.console) as live:
            while any(e.alive for e in self.game.enemies):
                # Ruch przeciwników po ścieżce (funkcyjnie: filter)
                for e in filter(lambda enemy: enemy.alive, self.game.enemies):
                    e.move(self.game.enemies)
                    if e.position == self.game.map.base:
                        self.process_enemy_base_entry(e)

                # Atak wież na przeciwników
                [t.attack(self.game.enemies) for t in self.game.towers]

                # Przyznawanie nagród (funkcyjnie: generator exp.)
                list(map(
                    self.process_enemy_reward,
                    filter(lambda e: not e.alive and not getattr(e, 'reached_end', False) and not getattr(e, 'rewarded', False), self.game.enemies)
                ))

                ui.refresh()
                live.update(ui.layout)
                time.sleep(max(0.1, 0.5 / self.game.game_speed))

            # Podsumowanie po fali
            defeated = sum(1 for e in self.game.enemies if getattr(e, 'rewarded', False))
            survived = sum(1 for e in self.game.enemies if getattr(e, 'reached_end', False))
            self.game.notifications.append(
                f"✔️ Fala {self.game.wave_number} zakończona: {defeated} pokonanych, {survived} przeżyło"
            )

        ui.simple_animated_event(
            f"FALA {self.game.wave_number} ZAKOŃCZONA!",
            emoji="🏁",
            color="bold green",
            hold_time=1.5
        )
        ui.refresh()
        self.game.save_game()
        self.game.notifications.append("💾 Gra automatycznie zapisana po ukończeniu fali.")
        input("\n⏸ Naciśnij Enter, aby kontynuować…")