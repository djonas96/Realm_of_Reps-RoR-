# Realm of Reps (RoR)

Trainingslog für Kraft und Laufen in der Konsole – mit XP, Level, Streaks und wöchentlichen Challenges.
Aufgabenbeschreibung: siehe [AUFGABE.md](AUFGABE.md).

## Starten

```
pip3 install -r requirements.txt
python3 main.py        # Konsolenmenü (für die Abgabe)
python3 gui.py         # grafisches Menü (Zusatz)
python3 test_ror.py    # Tests
```

Zum Ausprobieren mit Beispieldaten: `beispiel_training.csv` kopieren und in `training.csv` umbenennen.

## Dateien

| Datei | Wer | Inhalt |
|---|---|---|
| `daten_kraft.py` | Person A | CSV laden/speichern, Eingabe, Volumen pro Woche, Bestwerte |
| `lauf_gamification.py` | Person B | Pace, Wochenkilometer, XP, Level, Streak, Challenges, Plots |
| `main.py` | gemeinsam | Hauptmenü |
| `gui.py` | Zusatz | Grafisches Menü (tkinter/ttk) mit Kacheln, Tabs und eingebetteten Diagrammen |
| `wetter.py` | Zusatz | Trainingsplan nach Wetter (Open-Meteo, kein API-Key): Regen > 30 % → Kraft statt Lauf |
| `design.py` | Zusatz | Gemeinsame Farben für GUI und Plots (ruhig, gedecktes Grün) |
| `test_ror.py` | Zusatz | Einfache Tests ohne Zusatzbibliothek |
| `mobile/` | Zusatz | **RoR Mobile**: Handy-App als eine HTML-Datei, siehe [mobile/README.md](mobile/README.md) |
| `training.csv` | – | eure Trainingsdaten (wird beim ersten Eintrag angelegt) |

## Regeln (Version 1)

- **XP:** 10 pro Einheit, + 5 pro km (Lauf) bzw. + 1 pro 100 kg Volumen (Kraft)
- **Volumen:** Sätze × Wiederholungen × Gewicht
- **Level:** alle 100 XP ein Level
- **Streak:** aufeinanderfolgende Trainingstage bis heute (oder gestern)
- **Challenges:** 1–3 zufällige pro Kalenderwoche aus 5 Stück. Seed = Jahr × 100 + Woche (z. B. 202642), daher bleiben die Challenges nach einem Neustart gleich und sind am Handy dieselben. Erledigte Challenges geben Bonus-XP.

## Menü (`main.py`)

1 Workout eintragen · 2 Statistik · 3 Plot · 4 Level anzeigen · 5 Beenden (wie in der Angabe), dazu die Extras 6 Trainingsplan (Wetter) und 7 Letzten Eintrag löschen.
