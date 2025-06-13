def manhattan_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    """
    Zwraca dystans Manhattan pomiędzy dwoma punktami (x1, y1) oraz (x2, y2).
    Używany w logice wież do określania, czy wróg znajduje się w zasięgu.
    """
    return abs(x1 - x2) + abs(y1 - y2)


def clamp(value: int, min_value: int, max_value: int) -> int:
    """
    Ogranicza wartość value do przedziału [min_value, max_value].
    Użyteczne przy walidacji parametrów oraz przy obsłudze ruchu, hp itp.
    """
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value