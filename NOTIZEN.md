# Projekt-Notizen

Laufendes Protokoll: Was wurde gemacht, was wurde entschieden.

## 15.10.2026 – Erste Version

**Setup**
- Repo `djonas96/Realm_of_Reps-RoR-` (privat) mit Claude verbunden: GitHub-Connector in claude.ai plus Claude-GitHub-App unter github.com/apps/claude, Repo freigegeben
- Aufgabenbeschreibung aus dem Claude-Projekt „Vorbereitung Programmierprojekt“ als `AUFGABE.md` ins Repo gelegt
- Claude arbeitet in der Cloud: Code wird dort geschrieben, getestet und gepusht, der Laptop kann zu sein

**Entscheidungen**
- Ziel: Kurs bestehen, deshalb bewusst einfach: nur `csv`, `random`, `matplotlib`, kein pandas, keine Klassen
- Aufteilung nach `AUFGABE.md`: `daten_kraft.py` (Person A), `lauf_gamification.py` (Person B), `main.py` (gemeinsam)
- XP: 10 pro Einheit, + 5 pro km bzw. + 1 pro 100 kg Volumen; Level alle 100 XP
- Streak: aufeinanderfolgende Tage bis heute (oder gestern)
- Challenges: 1–3 pro Kalenderwoche aus 5, die Kalenderwoche ist der Zufalls-Seed (dadurch nach Neustart gleich, ohne Speichern). Alle 5 Typen werden geprüft.
- „Trainiere an 3 Tagen“ zählt verschiedene Tage, nicht Zeilen in der CSV

**Getestet** (automatisiert in der Cloud): alle Menüpunkte, Fehleingaben, leere Datei, alle 3 Plots

**Handy**
- Eine Swift-App lohnt sich nicht: zu viel Aufwand, und gratis läuft sie nur 7 Tage am iPhone
- Gratis-Optionen: a-Shell (Python im Terminal, Plots unsicher) oder später eine eigene HTML-Version (als Zusatz, nicht für die Abgabe)

## 16.10.2026 – Wetter-Trainingsplan

- Neue Datei `wetter.py`, im Menü als Punkt 6 (Punkte 1–5 bleiben wie in der Angabe)
- Holt die Regenwahrscheinlichkeit für die nächsten 5 Tage in Wien von Open-Meteo: gratis, kein API-Key, also kein Schlüssel im Repo
- Regel: Regen > 30 % oder keine Daten → Kraft, sonst Lauf
- Neue Abhängigkeit `requests` (in `requirements.txt`); am Mac einmal `pip3 install -r requirements.txt` ausführen
- Getestet: Logik mit Testwerten und Fehlermeldung ohne Internet. Den echten Abruf kann Claude aus der Cloud nicht testen, das bitte am Mac prüfen.

## 16.10.2026 – Grafisches Menü

- Neue Datei `gui.py` als **Zusatz**. `main.py` bleibt das Konsolenmenü laut Angabe (für die Abgabe).
- tkinter (bei Python dabei): Kopfzeile mit Level und Challenges, Buttons für Workout, Statistik, Level, Wetter-Plan, 3 Plots
- Workout-Eingabe als Formular mit Fehlermeldungen bei falschen Eingaben
- Nutzt dieselben Funktionen wie das Konsolenmenü, nichts doppelt programmiert
- Enthält eine Klasse (`RealmOfRepsApp`), falls OOP verlangt ist
- Start: `python3 gui.py`. Bei Homebrew-Python fehlt tkinter eventuell: `brew install python-tk`
- Getestet in der Cloud mit virtuellem Bildschirm: Anzeige, Statistik, Wetter-Plan (Testdaten), Formularprüfung

## Nachtschicht 15./16.10.2026 (Branch `nachtschicht`, Pull Request nach `main`)

**Python-Programm**
- `daten_kraft.py`: ungültige CSV-Zeilen werden übersprungen und gemeldet, statt dass das Programm abstürzt. Leere Übung, Datum in der Zukunft und Tippfehler beim Typ werden abgefangen (`k`/`l` geht auch). Zahlen werden ohne „.0“ gespeichert. Fehlt am Dateiende der Zeilenumbruch, wird er ergänzt. Neu: `letztes_workout_loeschen()`
- `lauf_gamification.py`:
  - **Bug:** 4,6 km gaben 22 statt 23 XP (Rundungsfehler bei Kommazahlen) → `abrunden()`
  - Challenge-Seed ist jetzt die Zahl `Jahr*100+Woche` statt Text, damit die Handy-App dieselben Challenges ziehen kann
  - Neu: `xp_balken()` (Fortschrittsbalken aus Textzeichen) und `challenge_wert()` (Fortschritt einer Challenge)
  - Plots: ruhiger Stil, Pace als m:ss (schneller = oben), Wochen ohne Training als 0 sichtbar. Die Zeichenfunktionen sind vom Fenster getrennt, damit die GUI sie einbetten kann.
- `main.py`: Überschriften mit Linien, XP-Balken, ✔/○ bei Challenges. Menü 1–5 wie in der Angabe, neu ist 7 „Letzten Eintrag löschen“. Strg+C beendet ohne Fehlermeldung.
- `wetter.py`: `plan_laden()` für Konsole und GUI, fängt auch unerwartete Antworten ab
- `gui.py`: neues Design mit ttk (Theme „clam“, damit die Farben auch am Mac wirken). Kacheln für Level, Streak, Woche und Challenges, Tabs für Eintragen, Statistik, Diagramme (im Fenster) und Wetter.
- `design.py` (neu): Farben für GUI, Plots und Handy-App an einer Stelle
- `test_ror.py` (neu): einfache Tests ohne Zusatzbibliothek, Start mit `python3 test_ror.py`

**RoR Mobile (`mobile/`)**
- `index.html` (die ganze App) plus `sw.js` (offline) und `icon.png` (Home-Bildschirm). Der Service Worker muss technisch eine eigene Datei sein, darum sind es 3 Dateien statt 1.
- Gleiche Regeln wie Python. Pythons Zufallsgenerator ist in JavaScript nachgebaut, damit es dieselben Challenges pro Woche gibt.
- CSV-Export und -Import im exakt gleichen Format wie `training.csv`. Daten liegen im localStorage, also nur am Gerät.
- Hosting: GitHub Pages ist gratis nur für öffentliche Repos → Empfehlung: eigenes öffentliches Repo `ror-mobile` mit nur den 3 Dateien (Anleitung in `mobile/README.md`)

**Entscheidungen**
- Nur Bibliotheken aus der Liste (csv, random, matplotlib, requests, tkinter). Für die Tests reicht `assert` statt pytest.
- Kraft-Farbe gedecktes Blau statt Grau, damit sie sich auch bei Farbschwäche vom Lauf-Grün unterscheidet
- `training.csv` bleibt vorerst im Repo (siehe „Morgen prüfen“)

**Getestet** (in der Cloud)
- `test_ror.py`: Rechnen, XP, Streak, Challenges, CSV (kaputte Zeile, Komma im Übungsnamen, fehlender Zeilenumbruch, Löschen), Wetter-Regel
- Konsole: alle Menüpunkte, Fehleingaben (Buchstaben, negative Zahlen, 13. Monat, Zukunft, leere Übung), ohne Datei, leere Eingabe am Ende
- Plots als Bild geprüft, GUI mit virtuellem Bildschirm (Formular, Fehlermeldung, Löschen, alle Tabs, ohne Daten)
- Handy-App im iPhone-Format (Chromium, hell und dunkel): Eintragen mit Fehleingaben, Import und Export (Datei identisch mit `beispiel_training.csv`), Diagramme, Wetter (Testdaten), offline neu laden
- JavaScript gegen Python: 300 Zufalls-Datensätze, 848 Wochen-Challenges und alle Tage 2019–2036 → 0 Abweichungen

**Bekannte Probleme / Grenzen**
- Durch den neuen Seed haben sich die Challenges aller Wochen geändert (Beispieldaten: 556 statt 586 XP)
- Echter Wetterabruf und das Aussehen am Mac sind nicht getestet. In der Cloud war das nicht möglich.
- Handy-App nur in Chromium getestet, nicht in Safari am echten iPhone
- Während das Wetter lädt (max. 10 s), reagiert die GUI nicht
- Mehrere Läufe am selben Tag ergeben im Pace-Plot eine senkrechte Linie
- Der Hinweis auf ungültige CSV-Zeilen erscheint in der Konsole bei jedem Menüdurchlauf

**Morgen prüfen bzw. entscheiden**
1. Pull Request durchsehen und mergen (siehe unten „Am Mac testen“)
2. `python3 main.py`, `python3 gui.py` und `python3 test_ror.py` am Mac starten
3. Ist der Menüpunkt 7 (Löschen) für die Abgabe ok, oder lieber nur in der GUI?
4. `training.csv` liegt im Repo und enthält genau die Beispieldaten. Entfernen und in `.gitignore` aufnehmen? Dann bleiben eigene Daten privat. Vorher eigene Einträge sichern!
5. Handy-App: Repo `ror-mobile` anlegen und am iPhone testen (Anleitung `mobile/README.md`)
6. Einträge in diesen Notizen mit Datum 16.10. stammen eigentlich vom 15.10. (Datum vorher falsch)

## Am Mac testen

1. GitHub Desktop: Repo klonen bzw. **Fetch origin → Pull**
2. **Repository → Open in Visual Studio Code**
3. Terminal in VS Code: `pip3 install -r requirements.txt` (einmalig)
4. Optional Beispieldaten: `beispiel_training.csv` duplizieren und in `training.csv` umbenennen
5. `python3 main.py` starten. Plot-Fenster schließen, damit es weitergeht.
6. `python3 gui.py` und `python3 test_ror.py` ausprobieren

## Offen

- Offizielle Angabe prüfen (Mindestanforderungen, Abgabeformat, Termin), siehe `AUFGABE.md` Abschnitt 5
- XP- und Level-Regeln gemeinsam abnicken
- Am Mac testen (inkl. Menüpunkt 6 mit echten Wetterdaten und `gui.py`)
- Handy-App (`mobile/`) am iPhone einrichten und testen
