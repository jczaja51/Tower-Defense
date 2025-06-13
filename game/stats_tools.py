import csv
import logging
from openpyxl import Workbook
import matplotlib.pyplot as plt

def export_stats_to_csv(stats, username, filename="statystyki.csv"):
    """
    Eksportuje statystyki gracza do pliku CSV.
    """
    try:
        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Statystyka", "Wartość"])
            for key, value in stats.items():
                writer.writerow([key, value])
        logging.info(f"Wyeksportowano statystyki gracza {username} do pliku {filename}")
        print(f"✅ Statystyki wyeksportowane do {filename}")
    except Exception as e:
        print(f"❌ Błąd eksportu do CSV: {e}")

def export_stats_to_excel(stats, username, filename="statystyki.xlsx"):
    """
    Eksportuje statystyki gracza do pliku Excel.
    """
    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "Statystyki"
        ws.append(["Statystyka", "Wartość"])
        for key, value in stats.items():
            ws.append([key, value])
        wb.save(filename)
        logging.info(f"Wyeksportowano statystyki gracza {username} do pliku {filename}")
        print(f"✅ Statystyki wyeksportowane do {filename}")
    except Exception as e:
        print(f"❌ Błąd eksportu do Excela: {e}")

def plot_stats_chart(stats):
    """
    Generuje wykres słupkowy ze statystyk gracza, wyświetlając liczby nad słupkami.
    """
    labels = list(stats.keys())
    values = list(stats.values())
    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values, color="skyblue")
    plt.xlabel("Statystyka")
    plt.ylabel("Wartość")
    plt.title("Twoje statystyki w grze")
    plt.xticks(rotation=20)

    # Liczby nad słupkami
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height,
                 f'{int(height)}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.show()