import csv
from openpyxl import load_workbook
from game.stats_tools import export_stats_to_csv, export_stats_to_excel, plot_stats_chart

def test_export_stats_to_csv(tmp_path):
    stats = {"zabici_przeciwnicy": 42, "wydane_zloto": 333}
    filename = tmp_path / "statystyki.csv"
    export_stats_to_csv(stats, "Tester", filename=str(filename))

    assert filename.exists()

    with open(filename, newline='') as csvfile:
        rows = list(csv.reader(csvfile))
        assert rows[0] == ["Statystyka", "Wartość"]
        assert rows[1] == ["zabici_przeciwnicy", "42"]
        assert rows[2] == ["wydane_zloto", "333"]

def test_export_stats_to_excel(tmp_path):
    stats = {"zabici_przeciwnicy": 11, "wydane_zloto": 222}
    filename = tmp_path / "statystyki.xlsx"
    export_stats_to_excel(stats, "Tester", filename=str(filename))

    assert filename.exists()

    wb = load_workbook(str(filename))
    ws = wb.active
    data = list(ws.values)
    assert data[0] == ("Statystyka", "Wartość")
    assert data[1] == ("zabici_przeciwnicy", 11)
    assert data[2] == ("wydane_zloto", 222)

def test_plot_stats_chart_runs(monkeypatch):
    import matplotlib
    matplotlib.use("Agg")
    stats = {"a": 1, "b": 2}
    plot_stats_chart(stats)