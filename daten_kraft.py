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

def zeile_gueltig(zeile):
    """Prueft eine CSV-Zeile. Nur gueltige Zeilen werden ausgewertet,
    damit ein Tippfehler in der Datei nicht das ganze Programm abstuerzen laesst."""
    try:
        date.fromisoformat(zeile["datum"])
        if zeile["typ"] == "kraft":
            return (int(zeile["saetze"]) > 0 and int(zeile["wdh"]) > 0
                    and float(zeile["gewicht"]) >= 0 and zeile["uebung"].strip() != "")
        if zeile["typ"] == "lauf":
            return float(zeile["km"]) > 0 and float(zeile["dauer_min"]) > 0
    except (ValueError, TypeError, KeyError):
        pass
    return False


def workouts_laden():
    """Liest alle gueltigen Workouts aus der CSV-Datei (Liste von Dictionaries).
    Ungueltige Zeilen werden uebersprungen und gemeldet."""
    if not os.path.exists(DATEI):
        return []
    # utf-8-sig: liest auch Dateien, die Excel mit unsichtbarem BOM-Zeichen speichert
    with open(DATEI, newline="", encoding="utf-8-sig") as datei:
        zeilen = list(csv.DictReader(datei))

    workouts = []
    for nummer, zeile in enumerate(zeilen, start=2):  # Zeile 1 = Ueberschrift
        if zeile_gueltig(zeile):
            workouts.append(zeile)
        else:
            print(f"Hinweis: Zeile {nummer} in {DATEI} ist ungültig und wird ignoriert.")
    return workouts


def zahl_text(wert):
    """Schreibt Zahlen ohne unnoetiges '.0' (60.0 -> '60', 62.5 -> '62.5')."""
    if wert == int(wert):
        return str(int(wert))
    return str(wert)


def workout_speichern(workout):
    """Haengt ein Workout an die CSV-Datei an (legt sie bei Bedarf neu an)."""
    neue_datei = not os.path.exists(DATEI) or os.path.getsize(DATEI) == 0
    if not neue_datei:
        # Fehlt am Dateiende der Zeilenumbruch (z. B. nach Bearbeiten im Editor),
        # wuerde die neue Zeile an die letzte angehaengt -> vorher Umbruch ergaenzen.
        with open(DATEI, "rb") as datei:
            datei.seek(-1, os.SEEK_END)
            fehlt_umbruch = datei.read(1) != b"\n"
        if fehlt_umbruch:
            with open(DATEI, "a", encoding="utf-8") as datei:
                datei.write("\n")

    zeile = {}
    for spalte in SPALTEN:
        wert = workout.get(spalte, "")
        zeile[spalte] = zahl_text(wert) if isinstance(wert, (int, float)) else wert

    with open(DATEI, "a", newline="", encoding="utf-8") as datei:
        writer = csv.DictWriter(datei, fieldnames=SPALTEN, lineterminator="\n")
        if neue_datei:
            writer.writeheader()
        writer.writerow(zeile)


def letztes_workout_loeschen():
    """Loescht den letzten Eintrag (z. B. nach einem Tippfehler).
    Gibt das geloeschte Workout zurueck oder None, wenn nichts da ist."""
    if not os.path.exists(DATEI):
        return None
    with open(DATEI, newline="", encoding="utf-8-sig") as datei:
        zeilen = list(csv.DictReader(datei))
    if not zeilen:
        return None
    geloescht = zeilen.pop()
    with open(DATEI, "w", newline="", encoding="utf-8") as datei:
        writer = csv.DictWriter(datei, fieldnames=SPALTEN, lineterminator="\n",
                                extrasaction="ignore")
        writer.writeheader()
        writer.writerows(zeilen)
    return geloescht


# ---------------------------------------------------------------
# Eingabe per input()
# ---------------------------------------------------------------

def zahl_eingeben(text, typ=float, null_erlaubt=False):
    """Fragt so lange nach, bis eine gueltige positive Zahl eingegeben wurde."""
    while True:
        try:
            wert = typ(input(text).strip().replace(",", "."))
        except ValueError:
            if typ == int:
                print("  Bitte eine ganze Zahl eingeben, z. B. 8.")
            else:
                print("  Bitte eine Zahl eingeben, z. B. 5 oder 5,5.")
            continue
        if wert > 0 or (null_erlaubt and wert == 0):
            return wert
        print("  Die Zahl muss größer als 0 sein." if not null_erlaubt
              else "  Die Zahl darf nicht negativ sein.")


def datum_eingeben():
    """Fragt ein Datum ab. Enter = heute. Datum in der Zukunft ist nicht erlaubt."""
    while True:
        text = input("Datum (JJJJ-MM-TT, Enter = heute): ").strip()
        if text == "":
            return date.today().isoformat()
        try:
            datum = datetime.strptime(text, "%Y-%m-%d").date()
        except ValueError:
            print("  Ungültiges Datum, Beispiel: 2026-10-15")
            continue
        if datum > date.today():
            print("  Das Datum liegt in der Zukunft.")
            continue
        return datum.isoformat()


def typ_eingeben():
    """Fragt den Trainingstyp ab: 'kraft' oder 'lauf' (k/l reicht auch)."""
    while True:
        typ = input("Typ (kraft/lauf): ").strip().lower()
        if typ in ("kraft", "k"):
            return "kraft"
        if typ in ("lauf", "l"):
            return "lauf"
        print("  Bitte 'kraft' oder 'lauf' eingeben.")


def text_eingeben(text):
    """Fragt einen Text ab, der nicht leer sein darf."""
    while True:
        eingabe = input(text).strip()
        if eingabe:
            return eingabe
        print("  Bitte etwas eingeben.")


def workout_hinzufuegen():
    """Fragt ein Workout per input() ab und speichert es in der CSV-Datei."""
    workout = {spalte: "" for spalte in SPALTEN}
    workout["datum"] = datum_eingeben()
    workout["typ"] = typ_eingeben()

    if workout["typ"] == "kraft":
        workout["uebung"] = text_eingeben("Übung (z. B. Bankdrücken): ")
        workout["saetze"] = zahl_eingeben("Sätze: ", int)
        workout["wdh"] = zahl_eingeben("Wiederholungen pro Satz: ", int)
        workout["gewicht"] = zahl_eingeben("Gewicht in kg (0 = Körpergewicht): ", null_erlaubt=True)
    else:
        workout["uebung"] = "Lauf"
        workout["km"] = zahl_eingeben("Distanz in km: ")
        workout["dauer_min"] = zahl_eingeben("Dauer in Minuten: ")

    workout_speichern(workout)
    print("✔ Workout gespeichert!")
    return workout


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
    """Hoechstes Gewicht je Uebung -> {'Bankdrücken': 70.0, ...}"""
    best = {}
    for w in workouts:
        if w["typ"] == "kraft":
            gewicht = float(w["gewicht"])
            if gewicht > best.get(w["uebung"], -1):
                best[w["uebung"]] = gewicht
    return best
