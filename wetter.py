"""
Trainingsplan abhängig vom Wetter: Regenwahrscheinlichkeit > 30 % -> kein Lauf, sondern Kraft.
Wetterdaten von Open-Meteo (gratis, kein API-Key nötig).
"""

from datetime import date

import requests

# Wien
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


def trainingsplan_anzeigen():
    """Lädt das Wetter und zeigt den Trainingsplan für die nächsten 5 Tage."""
    try:
        regen = regenwahrscheinlichkeit_laden()
    except requests.RequestException:
        print("Wetterdaten konnten nicht geladen werden (Internet?).")
        return

    print(f"\nTrainingsplan Wien (Lauf nur bis {REGEN_GRENZE} % Regen):")
    for datum, prozent, einheit in trainingsplan(regen):
        tag = WOCHENTAGE[date.fromisoformat(datum).weekday()]
        regen_text = "?" if prozent is None else f"{prozent} %"
        print(f"  {tag} {datum}: Regen {regen_text:>5} -> {einheit}")
