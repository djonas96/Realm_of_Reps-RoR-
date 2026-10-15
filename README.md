# Realm of Reps (RoR)

Trainingslog für Kraft und Laufen in der Konsole – mit XP, Level, Streaks und wöchentlichen Challenges.
Aufgabenbeschreibung: siehe [AUFGABE.md](AUFGABE.md).

## Starten

```
pip install -r requirements.txt
python main.py
```

Zum Ausprobieren mit Beispieldaten: `beispiel_training.csv` kopieren und in `training.csv` umbenennen.

## Dateien

| Datei | Wer | Inhalt |
|---|---|---|
| `daten_kraft.py` | Person A | CSV laden/speichern, Eingabe, Volumen pro Woche, Bestwerte |
| `lauf_gamification.py` | Person B | Pace, Wochenkilometer, XP, Level, Streak, Challenges, Plots |
| `main.py` | gemeinsam | Hauptmenü |
| `gui.py` | Zusatz | Grafisches Menü (tkinter): `python3 gui.py` |
| `wetter.py` | Zusatz | Trainingsplan nach Wetter (Open-Meteo, kein API-Key): Regen > 30 % → Kraft statt Lauf |
| `training.csv` | – | eure Trainingsdaten (wird beim ersten Eintrag angelegt) |

## Regeln (Version 1)

- **XP:** 10 pro Einheit, + 5 pro km (Lauf) bzw. + 1 pro 100 kg Volumen (Kraft)
- **Volumen:** Sätze × Wiederholungen × Gewicht
- **Level:** alle 100 XP ein Level
- **Streak:** aufeinanderfolgende Trainingstage bis heute (oder gestern)
- **Challenges:** 1–3 zufällige pro Kalenderwoche aus 5 Stück. Die Woche dient als Zufalls-Seed, daher bleiben die Challenges nach einem Neustart gleich. Erledigte Challenges geben Bonus-XP.
