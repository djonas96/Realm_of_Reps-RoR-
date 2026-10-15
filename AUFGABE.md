# Realm of Reps (RoR) – Aufgabenbeschreibung

> Stand: 15.10.2026. Zusammengefasst aus dem Claude-Projekt „Vorbereitung Programmierprojekt“.
> Hinweis: Die offizielle Aufgabenstellung (Angabe der Lehrveranstaltung) liegt im Projekt **nicht** vor. Punkte, die nur dort stehen können, sind unter „Offene Fragen“ gesammelt.

## 1. Aufgabenstellung und Ziel

- **Idee:** Python-Tool (Trainingslog) zur Erfassung und Auswertung von Kraft- und Lauftraining, mit Gamification (XP, Level, Streaks) und zufälligen Wochen-Challenges.
- **Ziel:** Training einfach protokollieren, Fortschritt sichtbar machen, durch Punkte, Streaks und Challenges motiviert bleiben.
- **Nutzen:** Hobbysportler behalten Kraft und Ausdauer in einem Tool im Blick, erkennen Stagnation, probieren Neues aus und bleiben dran.
- **Arbeitsform:** Projekt zu zweit (Person A / Person B, siehe Abschnitt 4).

## 2. Anforderungen und Vorgaben

### 2.1 Datenhaltung
- Eine CSV-Datei mit den Spalten:
  `datum, typ, uebung, saetze, wdh, gewicht, km, dauer_min`
- `typ` unterscheidet Kraft- und Laufeinheiten.
- Einlesen und Schreiben mit `csv` oder `pandas`.

### 2.2 Funktionen
| Bereich | Funktion | Zweck |
|---|---|---|
| Eingabe | `workout_hinzufuegen()` | Eingabe per `input()`, Speichern in CSV |
| Kraft | `volumen_pro_woche()` | Trainingsvolumen pro Woche |
| Kraft | `bestwerte()` | Bestleistungen je Übung |
| Lauf | `pace_berechnen()` | Pace aus km und Dauer |
| Lauf | `wochenkilometer()` | Kilometer pro Woche |
| Gamification | `xp_berechnen()` | XP aus Trainings |
| Gamification | `level()` | Level aus XP |
| Gamification | `streak()` | Serie aufeinanderfolgender Trainingstage |
| Challenges | `challenge_pruefen()` | Vergleicht CSV-Daten mit Challenge-Ziel |

### 2.3 Challenge-System
- **Pool:** Liste von Challenges als Dictionaries, z. B.
  `{"text": "Laufe 5 km", "typ": "lauf", "ziel": 5, "xp": 50}`
- **Auswahl:** `random.sample(pool, k)` mit `k = random.randint(1, 3)` → 1–3 zufällige Challenges, neu gezogen pro Woche (oder pro Tag).
- **Prüfung:** `challenge_pruefen()` vergleicht die CSV-Daten mit dem Ziel.
- **Belohnung:** Bonus-XP bei Erfüllung; Anzeige im Menü als „offen“ / „erledigt“.
- **Beispiel-Pool:**
  1. 5 km laufen
  2. 3 Workouts in dieser Woche
  3. 1000 kg Gesamtvolumen in einer Einheit
  4. Neue Bestpace
  5. 3 Tage Streak

### 2.4 Ein- und Ausgaben
- **Eingabe:** Konsole via `input()` (Workout-Daten, Menüauswahl).
- **Ausgabe:** Konsolentext (Statistiken, Level, XP, Challenge-Status) und matplotlib-Plots.
- **Plots:** Pace-Verlauf, Wochenkilometer, Kraftvolumen.

### 2.5 Menü
`while`-Schleife mit Auswahl:
1. Workout eintragen
2. Statistik
3. Plot
4. Level anzeigen
5. Beenden
- (Challenges offen/erledigt im Menü anzeigen)

### 2.6 Abgabeformat
- Nicht bekannt → siehe Offene Fragen.
- Code liegt im GitHub-Repo `djonas96/Realm_of_Reps-RoR-` (privat).

## 3. Technische Vorgaben

- **Sprache:** Python
- **Geplante Bibliotheken:** `csv` oder `pandas`, `matplotlib`, `random`
- **Python-Version:** nicht festgelegt → Offene Fragen
- **Erlaubte/verbotene Bibliotheken:** nicht festgelegt → Offene Fragen
- **Werkzeuge (Daniel):** Mac, Git über GitHub Desktop (kein Terminal-Workflow)

## 4. Bisherige Entscheidungen und Ideen

- Thema: Trainingslog Kraft + Lauf mit Gamification.
- Challenges werden integriert (1–3 zufällige pro Woche).
- **Umfang:** Zuerst 5 feste Challenges, Auswahl per `random`; Prüfung zunächst nur für 2 Typen:
  - Distanz (km)
  - Anzahl Workouts
  - Rest (Volumen, Bestpace, Streak) = Bonus.
- **Aufteilung zu zweit:**
  - Person A: Datenhaltung + Kraft-Auswertung
  - Person B: Läufe, Gamification, Plots
  - Danach gemeinsam das Menü zusammenbauen.

## 5. Offene Fragen

- [ ] Offizielle Angabe: Gibt es Mindestanforderungen (z. B. Anzahl Funktionen, Klassen/OOP, Fehlerbehandlung, Tests)?
- [ ] Python-Version?
- [ ] Erlaubte/verbotene Bibliotheken (z. B. `pandas`, `matplotlib`)?
- [ ] Abgabeformat und -termin (Repo-Link, ZIP, Doku, Präsentation)?
- [ ] `csv` oder `pandas` für die Datenhaltung?
- [ ] Challenges pro Woche oder pro Tag neu ziehen? Wie wird die Auswahl gespeichert, damit sie beim Neustart gleich bleibt?
- [ ] Formeln: XP pro Workout, Level-Schwellen, Streak-Definition (Kalendertage?)
- [ ] Wer ist Person A, wer Person B?
- [ ] Code-Editor (z. B. VS Code) schon installiert?
