"""
Einfache Tests ohne Zusatz-Bibliothek. Start mit:  python3 test_ror.py
Die Tests arbeiten mit einer eigenen Testdatei, training.csv bleibt unberuehrt.
"""

import os
from datetime import date, timedelta

import daten_kraft
from daten_kraft import volumen, kalenderwoche, bestwerte, volumen_pro_woche
from lauf_gamification import (pace_berechnen, pace_text, xp_fuer_workout, level, xp_balken,
                               streak, challenges_der_woche, challenge_pruefen,
                               wochen_auffuellen, laengste_serie)
from wetter import trainingsplan

TESTDATEI = "test_training.csv"


def lauf(datum, km, dauer):
    return {"datum": datum, "typ": "lauf", "uebung": "Lauf", "saetze": "", "wdh": "",
            "gewicht": "", "km": str(km), "dauer_min": str(dauer)}


def kraft(datum, saetze, wdh, gewicht, uebung="Bankdrücken"):
    return {"datum": datum, "typ": "kraft", "uebung": uebung, "saetze": str(saetze),
            "wdh": str(wdh), "gewicht": str(gewicht), "km": "", "dauer_min": ""}


def test_rechnen():
    assert volumen(kraft("2026-10-05", 4, 8, 62.5)) == 2000
    assert pace_berechnen(5, 27.5) == 5.5
    assert pace_text(5.5) == "5:30 min/km"
    assert pace_text(4.999) == "5:00 min/km"
    assert kalenderwoche("2026-10-15") == "2026-KW42"
    assert kalenderwoche("2027-01-01") == "2026-KW53"  # ISO-Woche gehoert noch zu 2026


def test_xp_und_level():
    assert xp_fuer_workout(lauf("2026-10-05", 4.6, 25)) == 10 + 23  # kein Rundungsfehler
    assert xp_fuer_workout(kraft("2026-10-05", 4, 8, 60)) == 10 + 19
    assert xp_fuer_workout(kraft("2026-10-05", 3, 8, 0)) == 10
    assert level(0) == 1 and level(99) == 1 and level(100) == 2
    assert xp_balken(130, breite=10).startswith("███░░░░░░░")


def test_streak():
    heute = date.today()
    tage = [(heute - timedelta(days=n)).isoformat() for n in (1, 2, 3)]
    assert streak([lauf(t, 5, 30) for t in tage]) == 3          # bis gestern zaehlt
    assert streak([lauf((heute - timedelta(days=2)).isoformat(), 5, 30)]) == 0
    assert laengste_serie({date(2026, 1, 1), date(2026, 1, 2), date(2026, 1, 5)}) == 2


def test_challenges():
    # gleiche Woche -> gleiche Challenges, 1 bis 3 Stueck
    for woche in range(1, 53):
        kw = f"2026-KW{woche:02d}"
        auswahl = challenges_der_woche(kw)
        assert auswahl == challenges_der_woche(kw)
        assert 1 <= len(auswahl) <= 3
    km_challenge = {"text": "", "typ": "km", "ziel": 5, "xp": 50}
    assert challenge_pruefen(km_challenge, [lauf("2026-10-12", 5, 30)], "2026-KW42")
    assert not challenge_pruefen(km_challenge, [lauf("2026-10-12", 4.9, 30)], "2026-KW42")
    pace_challenge = {"text": "", "typ": "bestpace", "ziel": 1, "xp": 60}
    alt = lauf("2026-10-05", 5, 25)  # 5:00 min/km
    assert not challenge_pruefen(pace_challenge, [alt, lauf("2026-10-12", 5, 26)], "2026-KW42")
    assert challenge_pruefen(pace_challenge, [alt, lauf("2026-10-12", 5, 24)], "2026-KW42")


def test_auswertung():
    workouts = [kraft("2026-10-05", 4, 8, 60), kraft("2026-10-12", 4, 8, 62.5),
                kraft("2026-10-12", 3, 8, 0, "Klimmzüge")]
    assert bestwerte(workouts) == {"Bankdrücken": 62.5, "Klimmzüge": 0}
    assert volumen_pro_woche(workouts) == {"2026-KW41": 1920, "2026-KW42": 2000}
    assert wochen_auffuellen({"2026-KW40": 5, "2026-KW42": 7}) == [
        ("2026-KW40", 5), ("2026-KW41", 0), ("2026-KW42", 7)]
    assert wochen_auffuellen({"2026-KW53": 1, "2027-KW01": 2}) == [("2026-KW53", 1), ("2027-KW01", 2)]


def test_wetter():
    plan = trainingsplan([("2026-10-16", 30), ("2026-10-17", 31), ("2026-10-18", None)])
    assert [einheit for _, _, einheit in plan] == ["Lauf", "Kraft", "Kraft"]


def test_csv():
    daten_kraft.DATEI = TESTDATEI
    try:
        assert daten_kraft.workouts_laden() == []                 # Datei fehlt
        assert daten_kraft.letztes_workout_loeschen() is None
        daten_kraft.workout_speichern({"datum": "2026-10-15", "typ": "lauf", "uebung": "Lauf",
                                       "km": 5.0, "dauer_min": 27.5})
        # Datei ohne Zeilenumbruch am Ende + eine kaputte Zeile
        with open(TESTDATEI, "a", encoding="utf-8") as datei:
            datei.write("2026-10-16,kraft,Kniebeuge,abc,8,80,,")
        daten_kraft.workout_speichern({"datum": "2026-10-17", "typ": "kraft",
                                       "uebung": "Rudern, Kurzhantel", "saetze": 3,
                                       "wdh": 10, "gewicht": 22.5})
        with open(TESTDATEI, encoding="utf-8") as datei:
            inhalt = datei.read()
        assert inhalt == ("datum,typ,uebung,saetze,wdh,gewicht,km,dauer_min\n"
                          "2026-10-15,lauf,Lauf,,,,5,27.5\n"
                          "2026-10-16,kraft,Kniebeuge,abc,8,80,,\n"
                          '2026-10-17,kraft,"Rudern, Kurzhantel",3,10,22.5,,\n')
        workouts = daten_kraft.workouts_laden()                   # kaputte Zeile wird uebersprungen
        assert len(workouts) == 2
        assert workouts[1]["uebung"] == "Rudern, Kurzhantel"
        assert daten_kraft.letztes_workout_loeschen()["datum"] == "2026-10-17"
        assert len(daten_kraft.workouts_laden()) == 1
    finally:
        daten_kraft.DATEI = "training.csv"
        if os.path.exists(TESTDATEI):
            os.remove(TESTDATEI)


if __name__ == "__main__":
    tests = [test_rechnen, test_xp_und_level, test_streak, test_challenges,
             test_auswertung, test_wetter, test_csv]
    for test in tests:
        test()
        print(f"OK  {test.__name__}")
    print("Alle Tests bestanden.")
