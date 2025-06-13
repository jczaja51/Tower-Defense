from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align
import time
import os
from rich import box
from game.building import Building

from game.stats_tools import (
    export_stats_to_csv,
    export_stats_to_excel,
    plot_stats_chart
)

class GameUI:
    """
    GameUI – klasa odpowiedzialna za interfejs tekstowy gry Tower Defense w terminalu (Rich).
    Zapewnia:
        -rysowanie mapy i panelu bocznego z aktualnym stanem gry,
        -animacje zdarzeń (np. start fali, cios krytyczny, stun, pauza),
        -eksport statystyk do pliku CSV/Excel oraz wykres (matplotlib),
        -obsługę wejścia użytkownika podczas rozgrywki,
        -dynamiczną prezentację powiadomień i efektów statusowych wrogów.
    """

    def __init__(self, game):
        """
        Inicjuje obiekt GameUI – buduje strukturę layoutu, ładuje konsolę Rich i
        integruje logikę budowania wież.
        """
        self.game = game
        self.console = Console()
        # Struktura layoutu: nagłówek, główny panel (mapa + sidebar)
        self.layout = Layout()
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
        )
        self.layout['main'].split_row(
            Layout(name="map", ratio=2),
            Layout(name="sidebar", ratio=1),
        )
        self.building = Building(self)

    def refresh(self):
        """
        Odświeża układ interfejsu (np. po ataku, budowie, zmianie statystyk).
        """
        self._update_layout()

    def effect_flash(self, msg, color="red", emoji="💥", repeat=2, speed=0.07):
        """
        Efekt krótkiego mignięcia tekstu na środku ekranu – np. przy ciosie krytycznym.
        """
        for _ in range(repeat):
            self.console.print(f"[bold {color}]{emoji} {msg} {emoji}[/]", justify="center")
            time.sleep(speed)
            self.console.clear()
            self._update_layout()
        self.console.print(f"[bold {color}]{emoji} {msg} {emoji}[/]", justify="center")
        time.sleep(0.4)

    def simple_animated_event(self, msg, emoji="💥", color="bold red", repeat=2, sleep_time=0.2, hold_time=1.0):
        """
        Uniwersalna animacja tekstowa dla ważnych zdarzeń (start/koniec fali, stun, boss).
        """
        for _ in range(repeat):
            self.console.clear()
            self.console.print(f"[{color}]{emoji} {msg} {emoji}[/{color}]", justify="center")
            time.sleep(sleep_time)
            self.console.clear()
            self._update_layout()
            time.sleep(sleep_time)
        self.console.print(f"[{color}]{emoji} {msg} {emoji}[/{color}]", justify="center")
        time.sleep(hold_time)



    def show_pause(self):
        """
        Wyświetla panel pauzy gry. Czyszczenie ekranu i informacja o zatrzymaniu.
        """
        os.system('cls' if os.name == 'nt' else 'clear')
        self.console.clear()
        panel = Panel(
            Align.center("[bold yellow]⏸ PAUZA ⏸\n\n[dim]Naciśnij Enter, aby wrócić do gry...[/]"),
            box=box.DOUBLE,
            width=40
        )
        self.console.print(panel, justify="center")
        input()

    def living_enemies(self):
        """Generator zwracający tylko żywych wrogów."""
        for enemy in self.game.enemies:
            if enemy.alive:
                yield enemy

    def _update_layout(self):
        """
        Buduje layout interfejsu – nagłówek, mapa, sidebar.
        Zawiera:
            -wyświetlanie mapy gry,
            -podsumowanie statystyk,
            -pasek HP i efekty statusowe wrogów,
            -powiadomienia,
            -kontrolki sterowania.
        """
        # Header
        header_padding = "\n" * 2
        self.layout['header'].update(
            Panel(
                Align.center(header_padding + "[bold cyan]🛡️  Tower Defense[/]"),
                box=box.ROUNDED,
                height=1
            )
        )

        # Mapa gry
        width = self.game.map.WIDTH
        height = self.game.map.HEIGHT

        lines = []
        lines.append("   " + " ".join(chr(65 + i) for i in range(width)))
        for i in range(height):
            row = f"{i + 1:2} "
            for j in range(width):
                ch = self.game.map.grid[i][j]
                # Zasięg wież i symbol wieży na planszy
                for t in self.game.towers:
                    if abs(i - t.y) + abs(j - t.x) <= t.range:
                        if (i, j) == (t.y, t.x):
                            ch = t.symbol
                        elif (i, j) in self.game.map.path:
                            ch = '.'
                # Przeciwnicy na planszy
                for e in self.game.enemies:
                    if e.alive and (i, j) == e.position:
                        ch = e.symbol
                row += ch + " "
            lines.append(row)

        map_str = "\n".join(lines)
        map_lines = len(lines)
        sidebar_min = 25
        panel_height = max(map_lines + 6, sidebar_min)

        self.layout['map'].update(
            Panel(
                Align.center(map_str, vertical="middle"),
                title="[bold]Mapa[/]",
                height=panel_height
            )
        )

        # Sidebar: statystyki, HP wrogów, kontrolki, powiadomienia
        stats = (
            f"[bold yellow]💰 Złoto:[/] {self.game.gold}\n"
            f"[bold red]❤️ Życia:[/] {self.game.lives}\n"
            f"[bold blue]🌊 Fala:[/] {self.game.wave_number}\n"
            f"[bold green]🕐 Tempo gry:[/] x{self.game.game_speed}\n"
        )

        bar_len = 10
        hp_lines = [
            f"{enemy.symbol} {enemy.name}: "
            f"[{('█' * int(enemy.hp / enemy.max_hp * bar_len) + '░' * (bar_len - int(enemy.hp / enemy.max_hp * bar_len)))}] "
            f"{enemy.hp}/{enemy.max_hp}"
            f"{' [red]🔥[/]' if getattr(enemy, 'burning', 0) > 0 else ''}"
            f"{' [blue]❄️[/]' if getattr(enemy, 'slowed', 0) > 0 else ''}"
            f"{' [yellow]💫[/]' if getattr(enemy, 'stunned', 0) > 0 else ''}"
            f"{' [magenta]👻[/]' if getattr(enemy, 'invisible', False) else ''}"
            f"{' [green]🩹[/]' if getattr(enemy, 'regenerates', False) and enemy.hp < enemy.max_hp else ''}"
            f"{' [cyan]🛡️[/]' if getattr(enemy, 'fire_immune', False) else ''}"
            for enemy in self.living_enemies()
        ]
        hp_text = "\n".join(hp_lines) or "Brak żywych wrogów"

        controls = (
            "[B] Buduj     [U] Ulepsz\n"
            "[+] Szybciej  [-] Wolniej\n"
            "[S] Zapisz    [A] Osiągnięcia\n"
            "[N] Fala      [M] Muzyka\n"
            "[E] Eksport   [P] Pauza\n"
            "[Q] Wyjście\n"
        )

        max_notif = 6
        to_show = self.game.notifications[-max_notif:]
        if len(to_show) < max_notif:
            to_show = [""] * (max_notif - len(to_show)) + to_show
        notif_text = "\n".join(f"[dim]{msg}[/]" for msg in to_show)

        sidebar_parts = [
            stats,
            "[bold]-- Przeciwnicy --[/]",
            hp_text,
            "[bold]-- Sterowanie --[/]",
            controls,
            "[bold]-- Powiadomienia --[/]",
            notif_text,
        ]
        sidebar_content = "\n\n".join(sidebar_parts)

        sidebar_panel = Panel(
            Align.center(sidebar_content, vertical="middle"),
            title="[bold]Panel boczny[/]",
            height=panel_height
        )
        self.layout['sidebar'].update(sidebar_panel)

    def run(self):
        """
        Główna pętla rozgrywki i obsługi wejścia użytkownika:
        umożliwia budowę i ulepszanie wież, start fal, eksport wyników, pauzę,
        sterowanie prędkością, zapisywanie gry, wyświetlanie osiągnięć i zakończenie gry.

        Obsługiwane klawisze:
            [B] – buduj wieżę
            [U] – ulepsz wieżę
            [N] – nowa fala
            [S] – zapis gry
            [E] – eksport statystyk
            [+] / [-] – tempo gry
            [M] – mute/unmute muzyki
            [A] – panel osiągnięć
            [P] – pauza
            [Q] – wyjście
        """
        if self.game.map is None:
            self.console.print("[red]❌ Nie zainicjalizowano mapy. Uruchom najpierw nową grę lub wczytaj zapis.[/]")
            return

        while self.game.lives > 0:
            os.system('cls' if os.name == 'nt' else 'clear')
            self.console.clear()
            self._update_layout()
            self.console.print(self.layout)

            choice = input("Wybierz opcję: ").strip().lower()

            if choice == 'a':
                self.game.show_achievements()
                input("\n⏸ Naciśnij Enter, aby wrócić do gry…")
            elif choice == 'b':
                self.game.building.build_tower()
            elif choice == 'u':
                self.game.building.upgrade_tower()
            elif choice == 'n':
                self.game.wave_loop.start_wave(self)
            elif choice == 's':
                self.game.save_game()
                self.game.notifications.append("💾 Zapisuję grę.")
                time.sleep(0.5)
            elif choice == 'm':
                self.game.sound.toggle_mute()
            elif choice == '+':
                self.game.game_speed = min(self.game.game_speed + 0.5, 5.0)
                self.game.notifications.append(f"⏩ Przyspieszono tempo: x{self.game.game_speed}")
            elif choice == '-':
                self.game.game_speed = max(self.game.game_speed - 0.5, 0.5)
                self.game.notifications.append(f"⏪ Spowolniono tempo: x{self.game.game_speed}")
            elif choice == 'e':
                while True:
                    print(
                        "\n[1] Eksportuj do CSV"
                        "\n[2] Eksportuj do Excel (XLSX)"
                        "\n[3] Eksportuj do obu"
                        "\n[4] Wyświetl wykres"
                        "\n[Q] Anuluj"
                    )
                    subchoice = input("Wybierz format eksportu / opcję: ").strip().lower()
                    if subchoice == '1':
                        export_stats_to_csv(self.game.stats, self.game.username)
                        break
                    elif subchoice == '2':
                        export_stats_to_excel(self.game.stats, self.game.username)
                        break
                    elif subchoice == '3':
                        export_stats_to_csv(self.game.stats, self.game.username)
                        export_stats_to_excel(self.game.stats, self.game.username)
                        break
                    elif subchoice == '4':
                        plot_stats_chart(self.game.stats)

                    elif subchoice == 'q':
                        print("❌ Anulowano eksport.")
                        break
                    else:
                        print("❌ Nieznana opcja.")
                input("⏸ Naciśnij Enter, aby wrócić do gry…")
            elif choice == 'p':
                self.show_pause()
            elif choice == 'q':
                os.system('cls' if os.name == 'nt' else 'clear')
                self.game.ranking.update_highscores()
                break
            else:
                self.game.notifications.append("❌ Nieznana opcja.")
            time.sleep(0.1)

            self.game.ranking.update_highscores()