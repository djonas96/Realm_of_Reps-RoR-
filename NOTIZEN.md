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

## Am Mac testen

1. GitHub Desktop: Repo klonen bzw. **Fetch origin → Pull**
2. **Repository → Open in Visual Studio Code**
3. Terminal in VS Code: `pip3 install -r requirements.txt` (einmalig)
4. Optional Beispieldaten: `beispiel_training.csv` duplizieren und in `training.csv` umbenennen
5. `python3 main.py` starten. Plot-Fenster schließen, damit es weitergeht.

## Offen

- Offizielle Angabe prüfen (Mindestanforderungen, Abgabeformat, Termin), siehe `AUFGABE.md` Abschnitt 5
- XP- und Level-Regeln gemeinsam abnicken
- Am Mac testen (inkl. Menüpunkt 6 mit echten Wetterdaten)
- Optional: HTML-Version fürs Handy
