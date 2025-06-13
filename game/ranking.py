import datetime
from rich.console import Console
from rich.table import Table
from rich import box
from game import database

class Ranking:
    """
        Klasa Ranking — obsługuje tablicę wyników (highscore) w grze Tower Defense.

        Odpowiedzialności:
            -obliczanie punktacji gracza na podstawie stanu gry,
            -zapisywanie i aktualizowanie rekordów w bazie,
            -czytelna prezentacja najlepszych wyników.
        """
    def __init__(self, game):
        """
        Inicjalizuje Ranking z referencją do aktualnej instancji gry.
        """
        self.game = game

    def calculate_score(self):
        """
        Oblicza łączną punktację gracza na podstawie liczby fal i zabitych przeciwników.
        """
        return self.game.wave_number * 50 + self.game.stats.get("zabici_przeciwnicy", 0) * 10

    def update_highscores(self):
        """
        Zapisuje aktualny wynik gracza do bazy i wyświetla ranking.
        """
        score = self.calculate_score()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        database.add_score(self.game.username, score, now)
        self.show_highscores()

    @staticmethod
    def show_highscores():
        """
        Wyświetla najlepsze wyniki z bazy w formie tabeli w konsoli (top 10).
        Jeśli nie ma żadnych wyników, informuje o tym użytkownika.
        """
        top_scores = database.get_top_scores()
        # top 10
        top_scores = sorted(top_scores, key=lambda hs: hs.score, reverse=True)[:10]
        console = Console()

        if not top_scores:
            console.print("[bold red]Brak wyników w rankingu.[/bold red]")
            return

        # Tworzenie tabeli wyników
        table = Table(
            title="🏆 [bold yellow]Najlepsze Wyniki[/bold yellow] 🏆",
            box=box.ROUNDED,
            border_style="bright_blue",
            show_lines=True,
            title_justify="center"
        )

        table.add_column("Miejsce", justify="center", style="bold white")
        table.add_column("Gracz", style="cyan", no_wrap=True, justify="center")
        table.add_column("Wynik", style="bold magenta", justify="center")
        table.add_column("Data", style="green", justify="center")

        medals = ["🥇", "🥈", "🥉"] + ["  "] * 7  # dla top 3

        for idx, entry in enumerate(top_scores):
            medal = medals[idx] if idx < 3 else f"{idx + 1}."
            row_style = "bold yellow" if idx == 0 else None
            table.add_row(
                medal,
                f"[b]{entry.username}[/b]",
                f"[b]{entry.score}[/b]",
                entry.date,
                style=row_style
            )

        console.print(table)