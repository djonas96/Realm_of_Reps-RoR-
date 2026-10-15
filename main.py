"""
Realm of Reps (RoR) - Trainingslog fuer Kraft und Laufen mit Gamification.
Gemeinsam: Hauptmenue. Start mit:  python3 main.py
"""

from datetime import date

from daten_kraft import (workouts_laden, workout_hinzufuegen, letztes_workout_loeschen,
                         volumen_pro_woche, bestwerte, kalenderwoche)
from lauf_gamification import (laeufe, pace_berechnen, pace_text, wochenkilometer,
                               xp_berechnen, level, xp_balken, streak,
                               challenges_der_woche, challenge_pruefen,
                               plot_pace, plot_wochenkilometer, plot_kraftvolumen)
from wetter import trainingsplan_anzeigen

BREITE = 44  # Breite der Trennlinien in Zeichen


def ueberschrift(text):
    """Gibt eine Ueberschrift mit Linie darunter aus."""
    print(f"\n{text}")
    print("─" * BREITE)


def challenges_anzeigen(workouts):
    """Zeigt die Challenges der aktuellen Woche mit Status offen/erledigt."""
    kw = kalenderwoche(date.today().isoformat())
    ueberschrift(f"Challenges {kw}")
    for challenge in challenges_der_woche(kw):
        if challenge_pruefen(challenge, workouts, kw):
            zeichen = "✔"
        else:
            zeichen = "○"
        print(f"  {zeichen} {challenge['text']}  (+{challenge['xp']} XP)")


def statistik_anzeigen(workouts):
    if not workouts:
        print("Noch keine Workouts eingetragen.")
        return

    ueberschrift("Kraft")
    volumen = volumen_pro_woche(workouts)
    if not volumen:
        print("  Noch keine Krafteinheiten.")
    for kw, vol in sorted(volumen.items()):
        print(f"  {kw}   {vol:>8.0f} kg Volumen")
    if volumen:
        print("\n  Bestwerte:")
    for uebung, gewicht in sorted(bestwerte(workouts).items()):
        if gewicht == 0:
            gewicht_text = "Körpergewicht"
        else:
            gewicht_text = f"{gewicht:g} kg"
        print(f"    {uebung:<16} {gewicht_text}")

    ueberschrift("Laufen")
    km = wochenkilometer(workouts)
    if not km:
        print("  Noch keine Läufe.")
    for kw, strecke in sorted(km.items()):
        print(f"  {kw}   {strecke:>8.1f} km")
    paces = [pace_berechnen(w["km"], w["dauer_min"]) for w in laeufe(workouts)]
    if paces:
        anzahl = "1 Lauf" if len(paces) == 1 else f"{len(paces)} Läufen"
        print(f"\n  Gesamt:      {sum(km.values()):.1f} km in {anzahl}")
        print(f"  Beste Pace:  {pace_text(min(paces))}")


def plot_auswahl(workouts):
    print("  1 = Pace-Verlauf   2 = Wochenkilometer   3 = Kraftvolumen")
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
    ueberschrift(f"Level {level(xp)}   ·   {xp} XP gesamt")
    print(f"  {xp_balken(xp)}")
    print(f"  Aktuelle Streak: {streak(workouts)} Tag(e)")


def letztes_loeschen():
    """Fragt nach und loescht dann den letzten Eintrag."""
    if input("Letzten Eintrag wirklich löschen? (j/n): ").strip().lower() != "j":
        print("Nichts gelöscht.")
        return
    geloescht = letztes_workout_loeschen()
    if geloescht is None:
        print("Es gibt noch keine Einträge.")
    else:
        print(f"Gelöscht: {geloescht['datum']} {geloescht['uebung']}")


def menue_anzeigen():
    print("\n" + "═" * BREITE)
    print("  1  Workout eintragen")
    print("  2  Statistik")
    print("  3  Plot")
    print("  4  Level anzeigen")
    print("  5  Beenden")
    print("  " + "-" * 20 + " Extras")
    print("  6  Trainingsplan (Wetter)")
    print("  7  Letzten Eintrag löschen")
    print("═" * BREITE)


def main():
    print("═" * BREITE)
    print("  REALM OF REPS  ·  Trainingslog mit XP")
    while True:
        workouts = workouts_laden()
        challenges_anzeigen(workouts)
        menue_anzeigen()
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
        elif auswahl == "7":
            letztes_loeschen()
        else:
            print("Bitte eine Zahl von 1 bis 7 eingeben.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        # Strg+C oder Ende der Eingabe: ohne Fehlermeldung beenden
        print("\nBis zum nächsten Training!")
