import random
from typing import List, Tuple
from game.config import MAP_WIDTH, MAP_HEIGHT

class Map:
    """Klasa Map – logika generowania i przechowywania planszy gry, ścieżki przeciwników i oznaczeń specjalnych"""
    SYMBOLS = {
        "empty": "█",
        "path":  "░",
        "base":  "⌂",
        "start": "◆"
    }

    def __init__(self, map_type: int = 1):
        """
        Inicjalizuje pustą siatkę oraz wybraną ścieżkę:
        """
        self.WIDTH: int = MAP_WIDTH
        self.HEIGHT: int = MAP_HEIGHT
        self.grid: List[List[str]] = [
            [self.SYMBOLS['empty'] for _ in range(self.WIDTH)]
            for _ in range(self.HEIGHT)
        ]
        self.path: List[Tuple[int, int]] = []
        self.start: Tuple[int, int] = (0, 0)
        self.base: Tuple[int, int] = (0, 0)

        # System wyboru generatora ścieżki
        generators = {
            1: self._generate_linear,
            2: self._generate_random,
            3: self._generate_diagonal
        }
        generator = generators.get(map_type, self._generate_linear)
        generator()
        self._place_markers()

    def _place_markers(self) -> None:
        """Oznacza na siatce start i bazę, bazując na wygenerowanej ścieżce."""
        if not self.path:
            return
        self.start = self.path[0]
        self.base = self.path[-1]
        sy, sx = self.start
        by, bx = self.base
        self.grid[sy][sx] = self.SYMBOLS['start']
        self.grid[by][bx] = self.SYMBOLS['base']

    def _generate_linear(self) -> None:
        """Tworzy prostą, pionową ścieżkę na środku planszy."""
        col = self.WIDTH // 2
        for row in range(self.HEIGHT):
            self.path.append((row, col))
            self.grid[row][col] = self.SYMBOLS['path']

    def _generate_random(self) -> None:
        """
        Generator losowej ścieżki z góry na dół, ze skrętami.
        Umożliwia tworzenie unikalnych plansz dla każdej rozgrywki.
        """
        x = random.randint(1, self.WIDTH - 2)
        y = 0
        self.path.append((y, x))
        self.grid[y][x] = self.SYMBOLS['path']

        attempts = 0
        while y < self.HEIGHT - 1:
            direction = random.choice(['down', 'left', 'right'])
            if direction == 'down' or attempts >= 5:
                y += 1
                attempts = 0
            elif direction == 'left' and x > 1:
                x -= 1
                attempts += 1
            elif direction == 'right' and x < self.WIDTH - 2:
                x += 1
                attempts += 1
            else:
                attempts += 1

            self.path.append((y, x))
            self.grid[y][x] = self.SYMBOLS['path']

    def _generate_diagonal(self) -> None:
        """Tworzy ścieżkę ukośną z lewego górnego rogu w dół na prawo."""
        x = y = 0
        while x < self.WIDTH and y < self.HEIGHT:
            self.path.append((y, x))
            self.grid[y][x] = self.SYMBOLS['path']
            x += 1
            y += 1