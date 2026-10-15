"""
Person A: Datenhaltung (CSV) und Kraft-Auswertung.
"""

import csv
import os
from datetime import date, datetime

DATEI = "training.csv"
SPALTEN = ["datum", "typ", "uebung", "saetze", "wdh", "gewicht", "km", "dauer_min"]


# ---------------------------------------------------------------
# Datenhaltung
# ---------------------------------------------------------------

def workouts_laden():
    """Liest alle Workouts aus der CSV-Datei (Liste von Dictionaries)."""
    if not os.path.exists(DATEI):
        return []
    with open(DATEI, newline="", encoding="utf-8") as datei:
        return list(csv.DictReader(datei))


def workout_speichern(workout):
    """Haengt ein Workout an die CSV-Datei an (legt sie bei Bedarf neu an)."""
    neue_datei = not os.path.exists(DATEI)
    with open(DATEI, "a", newline="", encoding="utf-8") as datei:
        writer = csv.DictWriter(datei, fieldnames=SPALTEN)
        if neue_datei:
            writer.writeheader()
        writer.writerow(workout)


def zahl_eingeben(text, typ=float, null_erlaubt=False):
    """Fragt so lange nach, bis eine gueltige positive Zahl eingegeben wurde."""
    while True:
        try:
            wert = typ(input(text).replace(",", "."))
        except ValueError:
            print("Bitte eine gültige Zahl eingeben.")
            continue
        if wert > 0 or (null_erlaubt and wert == 0):
            return wert
        print("Die Zahl muss größer als 0 sein.")


def datum_eingeben():
    """Fragt ein Datum ab. Enter = heute."""
    while True:
        text = input("Datum (JJJJ-MM-TT, Enter = heute): ").strip()
        if text == "":
            return date.today().isoformat()
        try:
            return datetime.strptime(text, "%Y-%m-%d").date().isoformat()
        except ValueError:
            print("Ungültiges Datum, Beispiel: 2026-10-15")


def workout_hinzufuegen():
    """Fragt ein Workout per input() ab und speichert es in der CSV-Datei."""
    workout = {spalte: "" for spalte in SPALTEN}
    workout["datum"] = datum_eingeben()

    typ = ""
    while typ not in ("kraft", "lauf"):
        typ = input("Typ (kraft/lauf): ").strip().lower()
    workout["typ"] = typ

    if typ == "kraft":
        workout["uebung"] = input("Übung (z. B. Bankdrücken): ").strip()
        workout["saetze"] = zahl_eingeben("Sätze: ", int)
        workout["wdh"] = zahl_eingeben("Wiederholungen pro Satz: ", int)
        workout["gewicht"] = zahl_eingeben("Gewicht in kg (0 = Körpergewicht): ", null_erlaubt=True)
    else:
        workout["uebung"] = "Lauf"
        workout["km"] = zahl_eingeben("Distanz in km: ")
        workout["dauer_min"] = zahl_eingeben("Dauer in Minuten: ")

    workout_speichern(workout)
    print("Workout gespeichert!")


# ---------------------------------------------------------------
# Hilfsfunktionen (werden auch von Person B verwendet)
# ---------------------------------------------------------------

def kalenderwoche(datum_text):
    """Macht aus '2026-10-15' den Text '2026-KW42'."""
    jahr, woche, _ = date.fromisoformat(datum_text).isocalendar()
    return f"{jahr}-KW{woche:02d}"


def volumen(workout):
    """Trainingsvolumen einer Kraft-Uebung: Saetze x Wiederholungen x Gewicht."""
    return int(workout["saetze"]) * int(workout["wdh"]) * float(workout["gewicht"])


# ---------------------------------------------------------------
# Kraft-Auswertung
# ---------------------------------------------------------------

def volumen_pro_woche(workouts):
    """Summiert das Kraftvolumen pro Kalenderwoche -> {'2026-KW42': 3200.0, ...}"""
    ergebnis = {}
    for w in workouts:
        if w["typ"] == "kraft":
            kw = kalenderwoche(w["datum"])
            ergebnis[kw] = ergebnis.get(kw, 0) + volumen(w)
    return ergebnis


def bestwerte(workouts):
    """Hoechstes Gewicht je Uebung -> {'Bankdruecken': 70.0, ...}"""
    best = {}
    for w in workouts:
        if w["typ"] == "kraft":
            gewicht = float(w["gewicht"])
            if gewicht > best.get(w["uebung"], -1):
                best[w["uebung"]] = gewicht
    return best
