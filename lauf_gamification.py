"""
Person B: Lauf-Auswertung, Gamification (XP, Level, Streak), Challenges und Plots.
"""

import random
from datetime import date, timedelta

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FuncFormatter

from daten_kraft import kalenderwoche, volumen, volumen_pro_woche
from design import FARBEN, SCHRIFT

XP_PRO_LEVEL = 100

# Schrift fuer Plots: die erste vorhandene wird genommen (Mac, Windows, Linux)
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = [SCHRIFT, "Arial", "DejaVu Sans"]


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

def abrunden(wert):
    """Rundet ab, gleicht aber winzige Rechenfehler von Kommazahlen aus
    (4.6 * 5 ergibt im Computer 22.999999... und soll trotzdem 23 sein)."""
    return int(wert + 0.000001)


def xp_fuer_workout(w):
    """10 XP pro Einheit + 5 XP pro km bzw. + 1 XP pro 100 kg Volumen."""
    if w["typ"] == "lauf":
        return 10 + abrunden(float(w["km"]) * 5)
    return 10 + abrunden(volumen(w) / 100)


def xp_berechnen(workouts):
    """Gesamt-XP aus allen Workouts plus Bonus-XP aus erledigten Challenges."""
    xp = 0
    for w in workouts:
        xp += xp_fuer_workout(w)
    return xp + bonus_xp(workouts)


def level(xp):
    """Alle 100 XP ein Level hoeher (Start bei Level 1)."""
    return xp // XP_PRO_LEVEL + 1


def xp_balken(xp, breite=20):
    """Fortschritt im aktuellen Level als Textbalken, z. B. '██████░░░░░░  30/100 XP'."""
    im_level = xp % XP_PRO_LEVEL
    voll = im_level * breite // XP_PRO_LEVEL
    return "█" * voll + "░" * (breite - voll) + f"  {im_level}/{XP_PRO_LEVEL} XP"


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
    """1-3 zufaellige Challenges fuer eine Woche (kw wie '2026-KW42').
    Der Zufall wird mit der Zahl 202642 (Jahr * 100 + Woche) gestartet (seed).
    Dadurch gibt es fuer dieselbe Woche immer dieselben Challenges,
    auch nach einem Neustart und auch in der Handy-App."""
    jahr, woche = kw.split("-KW")
    zufall = random.Random(int(jahr) * 100 + int(woche))
    k = zufall.randint(1, 3)
    return zufall.sample(CHALLENGE_POOL, k)


def challenge_wert(challenge, workouts, kw):
    """Wie weit ist die Challenge in Woche kw? Gibt den erreichten Wert zurueck."""
    diese_woche = [w for w in workouts if kalenderwoche(w["datum"]) == kw]
    typ = challenge["typ"]

    if typ == "km":
        return sum(float(w["km"]) for w in laeufe(diese_woche))

    if typ == "trainingstage":
        return len({w["datum"] for w in diese_woche})

    if typ == "volumen":
        pro_tag = {}
        for w in diese_woche:
            if w["typ"] == "kraft":
                pro_tag[w["datum"]] = pro_tag.get(w["datum"], 0) + volumen(w)
        return max(pro_tag.values(), default=0)

    if typ == "bestpace":
        frueher = [pace_berechnen(w["km"], w["dauer_min"]) for w in laeufe(workouts)
                   if kalenderwoche(w["datum"]) < kw]
        jetzt = [pace_berechnen(w["km"], w["dauer_min"]) for w in laeufe(diese_woche)]
        # Neue Bestpace = schnellster Lauf dieser Woche ist schneller als alle davor
        return 1 if jetzt and (not frueher or min(jetzt) < min(frueher)) else 0

    if typ == "streak":
        return laengste_serie({date.fromisoformat(w["datum"]) for w in diese_woche})

    return 0


def challenge_pruefen(challenge, workouts, kw):
    """Vergleicht die Workouts der Woche kw mit dem Ziel der Challenge."""
    return challenge_wert(challenge, workouts, kw) >= challenge["ziel"]


def bonus_xp(workouts):
    """Bonus-XP aller erledigten Challenges aus allen Wochen mit Training."""
    xp = 0
    for kw in {kalenderwoche(w["datum"]) for w in workouts}:
        for challenge in challenges_der_woche(kw):
            if challenge_pruefen(challenge, workouts, kw):
                xp += challenge["xp"]
    return xp


# ---------------------------------------------------------------
# Plots (schlichter Stil, gleiche Farben wie die GUI)
# ---------------------------------------------------------------

def stil_anwenden(ax, titel, y_text):
    """Einheitlicher, ruhiger Stil fuer alle Diagramme."""
    ax.figure.set_facecolor(FARBEN["karte"])
    ax.set_facecolor(FARBEN["karte"])
    ax.set_title(titel, loc="left", fontsize=13, color=FARBEN["text"], pad=12)
    ax.set_ylabel(y_text, color=FARBEN["text_leise"])
    for seite in ("top", "right", "left"):
        ax.spines[seite].set_visible(False)
    ax.spines["bottom"].set_color(FARBEN["linie"])
    ax.tick_params(colors=FARBEN["text_leise"], length=0)
    ax.grid(axis="y", color=FARBEN["linie"], linewidth=0.8)
    ax.set_axisbelow(True)


def wochen_auffuellen(werte_pro_woche):
    """Ergaenzt fehlende Wochen mit 0, damit Pausen im Diagramm sichtbar sind.
    {'2026-KW40': 5, '2026-KW42': 7} -> [('2026-KW40', 5), ('2026-KW41', 0), ('2026-KW42', 7)]"""
    if not werte_pro_woche:
        return []
    # Montag der ersten und der letzten Woche bestimmen
    montage = [date.fromisocalendar(int(kw[:4]), int(kw[-2:]), 1) for kw in werte_pro_woche]
    tag, ende = min(montage), max(montage)
    ergebnis = []
    while tag <= ende:
        kw = kalenderwoche(tag.isoformat())
        ergebnis.append((kw, werte_pro_woche.get(kw, 0)))
        tag += timedelta(days=7)
    return ergebnis


def zeichne_pace(ax, workouts):
    """Zeichnet den Pace-Verlauf in ax. Gibt False zurueck, wenn es keine Laeufe gibt."""
    liste = sorted(laeufe(workouts), key=lambda w: w["datum"])
    if not liste:
        return False
    daten = [date.fromisoformat(w["datum"]) for w in liste]
    paces = [pace_berechnen(w["km"], w["dauer_min"]) for w in liste]
    ax.plot(daten, paces, color=FARBEN["akzent"], linewidth=2, marker="o", markersize=7,
            markerfacecolor=FARBEN["akzent"], markeredgecolor=FARBEN["karte"], markeredgewidth=2)
    stil_anwenden(ax, "Pace-Verlauf", "min/km (oben = schneller)")
    ax.invert_yaxis()  # schneller (kleinere Pace) steht oben
    ax.xaxis.set_major_formatter(DateFormatter("%d.%m."))
    # y-Achse als Minuten:Sekunden statt Kommazahl (5.5 -> 5:30)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda wert, _: pace_text(wert).replace(" min/km", "")))
    # Beste Pace beschriften
    beste = paces.index(min(paces))
    ax.annotate(f"Best: {pace_text(paces[beste])}", (daten[beste], paces[beste]),
                textcoords="offset points", xytext=(0, 10), ha="center",
                fontsize=9, color=FARBEN["text"])
    ax.margins(x=0.08, y=0.2)
    return True


def zeichne_balken(ax, werte_pro_woche, farbe, titel, einheit):
    """Balkendiagramm pro Kalenderwoche (fuer Wochen-km und Kraftvolumen)."""
    wochen = wochen_auffuellen(werte_pro_woche)
    if not wochen:
        return False
    beschriftung = [kw.split("-")[1] for kw, _ in wochen]  # nur 'KW42'
    werte = [wert for _, wert in wochen]
    balken = ax.bar(beschriftung, werte, color=farbe, width=0.5)
    stil_anwenden(ax, titel, einheit)
    if len(werte) <= 12:
        ax.bar_label(balken, labels=[f"{w:g}" if w else "" for w in werte],
                     padding=3, fontsize=9, color=FARBEN["text"])
    ax.margins(y=0.15)
    return True


def zeichne_wochenkilometer(ax, workouts):
    km = {kw: round(wert, 1) for kw, wert in wochenkilometer(workouts).items()}
    return zeichne_balken(ax, km, FARBEN["akzent"], "Wochenkilometer", "km")


def zeichne_kraftvolumen(ax, workouts):
    vol = {kw: round(wert) for kw, wert in volumen_pro_woche(workouts).items()}
    return zeichne_balken(ax, vol, FARBEN["kraft"], "Kraftvolumen pro Woche", "kg")


def plot_zeigen(zeichenfunktion, workouts, meldung):
    """Oeffnet ein Plot-Fenster mit einer der zeichne_...-Funktionen."""
    figur, ax = plt.subplots(figsize=(8, 4.5))
    if not zeichenfunktion(ax, workouts):
        plt.close(figur)
        print(meldung)
        return
    figur.tight_layout()
    plt.show()


def plot_pace(workouts):
    plot_zeigen(zeichne_pace, workouts, "Noch keine Läufe eingetragen.")


def plot_wochenkilometer(workouts):
    plot_zeigen(zeichne_wochenkilometer, workouts, "Noch keine Läufe eingetragen.")


def plot_kraftvolumen(workouts):
    plot_zeigen(zeichne_kraftvolumen, workouts, "Noch keine Krafteinheiten eingetragen.")
