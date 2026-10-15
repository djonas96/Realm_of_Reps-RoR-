"""
Person B: Lauf-Auswertung, Gamification (XP, Level, Streak), Challenges und Plots.
"""

import random
from datetime import date, timedelta

import matplotlib.pyplot as plt

from daten_kraft import kalenderwoche, volumen, volumen_pro_woche


# ---------------------------------------------------------------
# Lauf-Auswertung
# ---------------------------------------------------------------

def laeufe(workouts):
    """Filtert nur die Laufeinheiten heraus."""
    return [w for w in workouts if w["typ"] == "lauf"]


def pace_berechnen(km, dauer_min):
    """Pace in Minuten pro Kilometer (z. B. 5.5 = 5:30 min/km)."""
    return float(dauer_min) / float(km)


def pace_text(pace):
    """Macht aus 5.5 den Text '5:30 min/km'."""
    minuten = int(pace)
    sekunden = round((pace - minuten) * 60)
    if sekunden == 60:
        minuten += 1
        sekunden = 0
    return f"{minuten}:{sekunden:02d} min/km"


def wochenkilometer(workouts):
    """Summiert die gelaufenen km pro Kalenderwoche -> {'2026-KW42': 12.5, ...}"""
    ergebnis = {}
    for w in laeufe(workouts):
        kw = kalenderwoche(w["datum"])
        ergebnis[kw] = ergebnis.get(kw, 0) + float(w["km"])
    return ergebnis


# ---------------------------------------------------------------
# Gamification
# ---------------------------------------------------------------

def xp_fuer_workout(w):
    """10 XP pro Einheit + 5 XP pro km bzw. + 1 XP pro 100 kg Volumen."""
    if w["typ"] == "lauf":
        return 10 + int(float(w["km"]) * 5)
    return 10 + int(volumen(w) / 100)


def xp_berechnen(workouts):
    """Gesamt-XP aus allen Workouts plus Bonus-XP aus erledigten Challenges."""
    xp = 0
    for w in workouts:
        xp += xp_fuer_workout(w)
    return xp + bonus_xp(workouts)


def level(xp):
    """Alle 100 XP ein Level hoeher (Start bei Level 1)."""
    return xp // 100 + 1


def laengste_serie(tage):
    """Laengste Folge aufeinanderfolgender Kalendertage in einer Menge von Daten."""
    laengste = 0
    for tag in tage:
        # Nur bei einem Serien-Anfang zu zaehlen beginnen
        if tag - timedelta(days=1) in tage:
            continue
        laenge = 1
        while tag + timedelta(days=laenge) in tage:
            laenge += 1
        laengste = max(laengste, laenge)
    return laengste


def streak(workouts):
    """Aktuelle Serie: aufeinanderfolgende Trainingstage bis heute (oder gestern)."""
    tage = {date.fromisoformat(w["datum"]) for w in workouts}
    tag = date.today()
    if tag not in tage:
        tag -= timedelta(days=1)  # heute noch nicht trainiert -> Serie zaehlt bis gestern
    anzahl = 0
    while tag in tage:
        anzahl += 1
        tag -= timedelta(days=1)
    return anzahl


# ---------------------------------------------------------------
# Challenges
# ---------------------------------------------------------------

CHALLENGE_POOL = [
    {"text": "Laufe 5 km", "typ": "km", "ziel": 5, "xp": 50},
    {"text": "Trainiere an 3 verschiedenen Tagen", "typ": "trainingstage", "ziel": 3, "xp": 40},
    {"text": "Schaffe 1000 kg Kraftvolumen an einem Tag", "typ": "volumen", "ziel": 1000, "xp": 40},
    {"text": "Laufe eine neue Bestpace", "typ": "bestpace", "ziel": 1, "xp": 60},
    {"text": "Trainiere 3 Tage hintereinander", "typ": "streak", "ziel": 3, "xp": 50},
]


def challenges_der_woche(kw):
    """1-3 zufaellige Challenges fuer eine Woche.
    Der Zufall wird mit der Kalenderwoche gestartet (seed), deshalb gibt es
    fuer dieselbe Woche immer dieselben Challenges - auch nach einem Neustart."""
    zufall = random.Random(kw)
    k = zufall.randint(1, 3)
    return zufall.sample(CHALLENGE_POOL, k)


def challenge_pruefen(challenge, workouts, kw):
    """Vergleicht die Workouts der Woche kw mit dem Ziel der Challenge."""
    diese_woche = [w for w in workouts if kalenderwoche(w["datum"]) == kw]
    typ = challenge["typ"]

    if typ == "km":
        wert = sum(float(w["km"]) for w in laeufe(diese_woche))

    elif typ == "trainingstage":
        wert = len({w["datum"] for w in diese_woche})

    elif typ == "volumen":
        pro_tag = {}
        for w in diese_woche:
            if w["typ"] == "kraft":
                pro_tag[w["datum"]] = pro_tag.get(w["datum"], 0) + volumen(w)
        wert = max(pro_tag.values(), default=0)

    elif typ == "bestpace":
        frueher = [pace_berechnen(w["km"], w["dauer_min"]) for w in laeufe(workouts)
                   if kalenderwoche(w["datum"]) < kw]
        jetzt = [pace_berechnen(w["km"], w["dauer_min"]) for w in laeufe(diese_woche)]
        # Neue Bestpace = schnellster Lauf dieser Woche ist schneller als alle davor
        wert = 1 if jetzt and (not frueher or min(jetzt) < min(frueher)) else 0

    elif typ == "streak":
        wert = laengste_serie({date.fromisoformat(w["datum"]) for w in diese_woche})

    else:
        wert = 0

    return wert >= challenge["ziel"]


def bonus_xp(workouts):
    """Bonus-XP aller erledigten Challenges aus allen Wochen mit Training."""
    xp = 0
    for kw in {kalenderwoche(w["datum"]) for w in workouts}:
        for challenge in challenges_der_woche(kw):
            if challenge_pruefen(challenge, workouts, kw):
                xp += challenge["xp"]
    return xp


# ---------------------------------------------------------------
# Plots
# ---------------------------------------------------------------

def plot_pace(workouts):
    liste = sorted(laeufe(workouts), key=lambda w: w["datum"])
    if not liste:
        print("Noch keine Läufe eingetragen.")
        return
    daten = [w["datum"] for w in liste]
    paces = [pace_berechnen(w["km"], w["dauer_min"]) for w in liste]
    plt.plot(daten, paces, marker="o")
    plt.title("Pace-Verlauf")
    plt.ylabel("min/km (kleiner = schneller)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_wochenkilometer(workouts):
    km = wochenkilometer(workouts)
    if not km:
        print("Noch keine Läufe eingetragen.")
        return
    wochen = sorted(km)
    plt.bar(wochen, [km[kw] for kw in wochen])
    plt.title("Wochenkilometer")
    plt.ylabel("km")
    plt.tight_layout()
    plt.show()


def plot_kraftvolumen(workouts):
    vol = volumen_pro_woche(workouts)
    if not vol:
        print("Noch keine Krafteinheiten eingetragen.")
        return
    wochen = sorted(vol)
    plt.bar(wochen, [vol[kw] for kw in wochen])
    plt.title("Kraftvolumen pro Woche")
    plt.ylabel("kg")
    plt.tight_layout()
    plt.show()
