"""
Trainingsplan abhängig vom Wetter: Regenwahrscheinlichkeit > 30 % -> kein Lauf, sondern Kraft.
Wetterdaten von Open-Meteo (gratis, kein API-Key nötig).
"""

from datetime import date

import requests

# Wien
ORT = "Wien"
BREITENGRAD = 48.21
LAENGENGRAD = 16.37
REGEN_GRENZE = 30  # Prozent

WOCHENTAGE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def regenwahrscheinlichkeit_laden(tage=5):
    """Holt die maximale Regenwahrscheinlichkeit pro Tag.
    Gibt eine Liste von (datum, prozent) zurück, z. B. [("2026-10-16", 20), ...]."""
    url = "https://api.open-meteo.com/v1/forecast"
    parameter = {
        "latitude": BREITENGRAD,
        "longitude": LAENGENGRAD,
        "daily": "precipitation_probability_max",
        "timezone": "Europe/Vienna",
        "forecast_days": tage,
    }
    antwort = requests.get(url, params=parameter, timeout=10)
    antwort.raise_for_status()
    daten = antwort.json()["daily"]
    return list(zip(daten["time"], daten["precipitation_probability_max"]))


def trainingsplan(regen_pro_tag):
    """Macht aus [(datum, prozent), ...] einen Plan [(datum, prozent, einheit), ...].
    Regen über der Grenze (oder keine Daten) -> Kraft, sonst Lauf."""
    plan = []
    for datum, prozent in regen_pro_tag:
        if prozent is None or prozent > REGEN_GRENZE:
            einheit = "Kraft"
        else:
            einheit = "Lauf"
        plan.append((datum, prozent, einheit))
    return plan


def plan_laden():
    """Lädt das Wetter und gibt den Plan zurück, oder None ohne Internet.
    Wird von der Konsole und von der GUI verwendet."""
    try:
        return trainingsplan(regenwahrscheinlichkeit_laden())
    except (requests.RequestException, KeyError, ValueError):
        # RequestException: kein Internet / Server-Fehler
        # KeyError, ValueError: Antwort hat ein unerwartetes Format
        return None


def plan_zeile(datum, prozent, einheit):
    """Eine Zeile des Plans als Text, z. B. 'Fr 16.10.   Regen  20 %  →  Lauf'."""
    tag = date.fromisoformat(datum)
    regen_text = "  ?" if prozent is None else f"{prozent:>3}"
    return f"{WOCHENTAGE[tag.weekday()]} {tag:%d.%m.}   Regen {regen_text} %  →  {einheit}"


def trainingsplan_anzeigen():
    """Zeigt den Trainingsplan für die nächsten 5 Tage in der Konsole."""
    plan = plan_laden()
    if plan is None:
        print("Wetterdaten konnten nicht geladen werden (Internet?).")
        return
    print(f"\nTrainingsplan {ORT} (Lauf nur bis {REGEN_GRENZE} % Regen)")
    print("─" * 44)
    for datum, prozent, einheit in plan:
        print("  " + plan_zeile(datum, prozent, einheit))
