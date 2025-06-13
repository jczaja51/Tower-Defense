Konsolowy Tower Defense

Tower Defense to strategiczna gra, w której gracz broni swojej bazy przed falami przeciwników poruszających się po wyznaczonej ścieżce. Gracz buduje różne rodzaje wież obronnych, które automatycznie atakują zbliżających się wrogów. Każda wieża ma unikalne właściwości, zasięg ataku, szybkość strzelania oraz koszt. Przeciwnicy różnią się statystykami (zdrowie, szybkość, odporność na określone typy ataków) i z każdą falą stają się silniejsi. Gra wykorzystuje reprezentację planszy za pomocą znaków ASCII, z różnymi symbolami dla wież, przeciwników i ścieżek. System ekonomiczny pozwala zdobywać złoto za pokonanych wrogów i wydawać je na budowę nowych wież lub ulepszanie istniejących. Gracz musi strategicznie planować rozmieszczenie wież, zarządzać ograniczonymi zasobami i adaptować strategię do zmieniających się warunków, aby przetrwać jak najwięcej fal przeciwników.


Funkcje gry
-Rozgrywka turowa: Bronisz się przed kolejnymi falami przeciwników na różnych typach map.

-Wieże: 5 typów wież, każda z własną specjalną zdolnością.

-Ulepszanie: Wieże można ulepszać (lepsze statystyki, większy zasięg, nowe efekty).

-Przeciwnicy: Kilka rodzajów wrogów (m.in. gobliny, orki, smoki, bossowie), z różnymi cechami i odpornościami.

-Ranking: Najlepsze wyniki zapisywane są w bazie (możesz pobijać swoje i cudze rekordy).

-Osiągnięcia: Trzy podstawowe osiągnięcia (100 pokonanych, 1000 zł, 20 wież).

-Eksport statystyk: Wyniki możesz zapisać do pliku CSV, XLSX lub zobaczyć wykres statystyk.

-Dźwięk i muzyka: Zmiana głośności efektów i tła muzycznego (z możliwością wyciszenia).

-Personalizacja: Własne ustawienia trudności i parametrów rozgrywki, wybór mapy, nick gracza.

-Interfejs Rich: Kolorowy, dynamiczny UI (panel boczny, powiadomienia, paski HP, efekty emoji).



Jak zainstalować i uruchomić grę?

1. Wymagania
Python 3.9+
System: Windows, Linux, MacOS


2. Instalacja zależności
Zalecane jest utworzenie wirtualnego środowiska:

python3 -m venv venv

source venv/bin/activate   # Linux/Mac

venv\Scripts\activate      # Windows


Instalacja paczek:

pip3 install -r requirements.txt    # Linux/Mac

pip install -r requirements.txt     # Windows



3. Uruchamianie gry

Podstawowe uruchomienie:

python3 main.py  # Linux/Mac

python main.py   # Windows


Argumenty wiersza poleceń:

--mute – wycisza wszystkie dźwięki

--nick NICK – ustaw nick gracza przy starcie

Przykład:

python3 main.py --mute --nick NoobMaster   # Linux/Mac

python main.py --mute --nick NoobMaster    # Windows



4. Obsługa gry (sterowanie w trakcie rozgrywki)

[B] – Buduj wieżę
[U] – Ulepsz wieżę
[N] – Następna fala
[A] – Zobacz osiągnięcia
[S] – Zapisz grę
[E] – Eksportuj statystyki (CSV/XLSX/wykres)
[M] – Wycisz/odcisz muzykę
[P] – Pauza
[+] – Przyspiesz rozgrywkę
[-] – Spowolnij rozgrywkę
[Q] – Wyjście (z zapisaniem wyniku do rankingu)


Typy map

Liniowa: Prosta trasa środkiem planszy
Losowa: Trasa ze skrętami (większa różnorodność)
Diagonalna: Ukośna linia z lewego górnego rogu


Typy wież i efekty specjalne

Strzelająca: Atak krytyczny co 5 strzał, zadaje podwójne obrażenia.
Ciężka Armatnia: Szansa na ogłuszenie przeciwnika.
Lodowa: Spowalnia wrogów.
Magia Ognia: Podpala wrogów.
Laserowa: Przebija wrogów i może atakować duchy.


Przeciwnicy

Goblin, Ork, Troll (regenerujący), Duch (niewidzialny), Smok (boss), Nietoperz (latający), Pająk, Rycerz (odporny na ogień)
Każdy typ ma inne statystyki, odporności i czasem własne umiejętności.


Ranking i osiągnięcia

Ranking widoczny z poziomu menu gry oraz w trakcie.
Osiągnięcia (pokonani, złoto, zbudowane wieże) widoczne w panelu.


Eksport i analiza wyników

Eksport statystyk do pliku .csv, .xlsx lub prezentacja w formie wykresu (słupki).
Statystyki: liczba pokonanych, zbudowane wieże, wydane złoto, maks. posiadane złoto itd.


Dźwięk i muzyka

Efekty dźwiękowe dla akcji (strzał, zbudowanie wieży, pokonanie, utrata życia)
Muzyka w tle – domyślnie włączona, można wyciszyć ([M] lub --mute)


Konfiguracja i ustawienia

Preferencje (trudność, fale, złoto, życie, głośność) — menu gry, zapis do preferences.json i bazy tower_defense.db


Zapis/odczyt gry

Gra umożliwia zapis w kilku slotach, wczytywanie i usuwanie zapisów.
Zapis obejmuje całą mapę, statystyki, wieże i postęp.


Testowanie projektu

Aby uruchomić testy jednostkowe i integracyjne, przejdź do katalogu głównego projektu i użyj:

pytest tests/

Aby sprawdzić pokrycie kodu testami uruchom:

pytest --cov=game tests/

Wynik pokaże procent pokrycia testami dla wszystkich plików w folderze game/.

Autor
Jakub Czaja