"""
Realm of Reps (RoR) - Trainingslog fuer Kraft und Laufen mit Gamification.
Gemeinsam: Hauptmenue. Start mit:  python main.py
"""

from datetime import date

from daten_kraft import workouts_laden, workout_hinzufuegen, volumen_pro_woche, bestwerte, kalenderwoche
from lauf_gamification import (laeufe, pace_berechnen, pace_text, wochenkilometer,
                               xp_berechnen, level, streak,
                               challenges_der_woche, challenge_pruefen,
                               plot_pace, plot_wochenkilometer, plot_kraftvolumen)
from wetter import trainingsplan_anzeigen


def challenges_anzeigen(workouts):
    """Zeigt die Challenges der aktuellen Woche mit Status offen/erledigt."""
    kw = kalenderwoche(date.today().isoformat())
    print(f"\nChallenges {kw}:")
    for challenge in challenges_der_woche(kw):
        status = "erledigt" if challenge_pruefen(challenge, workouts, kw) else "offen"
        print(f"  [{status:8}] {challenge['text']} (+{challenge['xp']} XP)")


def statistik_anzeigen(workouts):
    if not workouts:
        print("Noch keine Workouts eingetragen.")
        return

    print("\n--- Kraft ---")
    for kw, vol in sorted(volumen_pro_woche(workouts).items()):
        print(f"  {kw}: {vol:.0f} kg Volumen")
    print("  Bestwerte:")
    for uebung, gewicht in bestwerte(workouts).items():
        print(f"    {uebung}: {gewicht:g} kg")

    print("\n--- Laufen ---")
    for kw, km in sorted(wochenkilometer(workouts).items()):
        print(f"  {kw}: {km:.1f} km")
    paces = [pace_berechnen(w["km"], w["dauer_min"]) for w in laeufe(workouts)]
    if paces:
        print(f"  Beste Pace: {pace_text(min(paces))}")


def plot_auswahl(workouts):
    print("1 = Pace-Verlauf, 2 = Wochenkilometer, 3 = Kraftvolumen")
    auswahl = input("Welcher Plot? ").strip()
    if auswahl == "1":
        plot_pace(workouts)
    elif auswahl == "2":
        plot_wochenkilometer(workouts)
    elif auswahl == "3":
        plot_kraftvolumen(workouts)
    else:
        print("Ungültige Auswahl.")


def level_anzeigen(workouts):
    xp = xp_berechnen(workouts)
    print(f"\nLevel {level(xp)}  |  {xp} XP  |  noch {100 - xp % 100} XP bis zum nächsten Level")
    print(f"Aktuelle Streak: {streak(workouts)} Tag(e)")


def main():
    print("=== Realm of Reps ===")
    while True:
        workouts = workouts_laden()
        challenges_anzeigen(workouts)
        print("\n1 Workout eintragen")
        print("2 Statistik")
        print("3 Plot")
        print("4 Level anzeigen")
        print("5 Beenden")
        print("6 Trainingsplan (Wetter)")
        auswahl = input("Auswahl: ").strip()

        if auswahl == "1":
            workout_hinzufuegen()
        elif auswahl == "2":
            statistik_anzeigen(workouts)
        elif auswahl == "3":
            plot_auswahl(workouts)
        elif auswahl == "4":
            level_anzeigen(workouts)
        elif auswahl == "5":
            print("Bis zum nächsten Training!")
            break
        elif auswahl == "6":
            trainingsplan_anzeigen()
        else:
            print("Bitte 1-6 eingeben.")


if __name__ == "__main__":
    main()
