"""
Grafisches Menü für Realm of Reps (Zusatz zu main.py).
Start mit:  python3 gui.py
Nutzt tkinter (bei Python schon dabei) und dieselben Funktionen wie das Konsolenmenü.
"""

import io
import tkinter as tk
from contextlib import redirect_stdout
from datetime import date, datetime
from tkinter import messagebox

import matplotlib
matplotlib.use("TkAgg")  # Plots als Tk-Fenster, passt zum GUI

from daten_kraft import SPALTEN, workout_speichern, workouts_laden
from lauf_gamification import plot_kraftvolumen, plot_pace, plot_wochenkilometer
from main import challenges_anzeigen, level_anzeigen, statistik_anzeigen
from wetter import trainingsplan_anzeigen


def ausgabe_von(funktion, *argumente):
    """Führt eine Funktion aus, die mit print() arbeitet, und gibt den Text zurück."""
    puffer = io.StringIO()
    with redirect_stdout(puffer):
        funktion(*argumente)
    return puffer.getvalue().strip()


class RealmOfRepsApp:
    def __init__(self, fenster):
        self.fenster = fenster
        fenster.title("Realm of Reps")
        fenster.geometry("560x520")

        # Kopfzeile mit Level und Challenges
        self.kopf = tk.Label(fenster, justify="left", anchor="w", font=("Helvetica", 13))
        self.kopf.pack(fill="x", padx=12, pady=(12, 4))

        # Buttons
        leiste = tk.Frame(fenster)
        leiste.pack(fill="x", padx=12, pady=6)
        knoepfe = [
            ("Workout eintragen", self.workout_fenster),
            ("Statistik", lambda: self.zeigen(statistik_anzeigen, workouts_laden())),
            ("Level", lambda: self.zeigen(level_anzeigen, workouts_laden())),
            ("Wetter-Plan", lambda: self.zeigen(trainingsplan_anzeigen)),
        ]
        for spalte, (text, befehl) in enumerate(knoepfe):
            tk.Button(leiste, text=text, command=befehl).grid(row=0, column=spalte, padx=2, sticky="ew")
            leiste.columnconfigure(spalte, weight=1)

        plots = tk.Frame(fenster)
        plots.pack(fill="x", padx=12)
        tk.Label(plots, text="Plots:").pack(side="left")
        tk.Button(plots, text="Pace", command=lambda: plot_pace(workouts_laden())).pack(side="left", padx=2)
        tk.Button(plots, text="Wochen-km", command=lambda: plot_wochenkilometer(workouts_laden())).pack(side="left", padx=2)
        tk.Button(plots, text="Kraftvolumen", command=lambda: plot_kraftvolumen(workouts_laden())).pack(side="left", padx=2)

        # Ausgabefeld
        self.textfeld = tk.Text(fenster, height=15, font=("Courier", 12))
        self.textfeld.pack(fill="both", expand=True, padx=12, pady=12)

        self.kopf_aktualisieren()

    def kopf_aktualisieren(self):
        workouts = workouts_laden()
        text = ausgabe_von(level_anzeigen, workouts) + "\n" + ausgabe_von(challenges_anzeigen, workouts)
        self.kopf.config(text=text)

    def zeigen(self, funktion, *argumente):
        """Schreibt die Ausgabe einer Funktion ins Textfeld."""
        self.textfeld.delete("1.0", tk.END)
        self.textfeld.insert(tk.END, ausgabe_von(funktion, *argumente))

    def workout_fenster(self):
        """Eigenes Fenster mit Formular für ein neues Workout."""
        dialog = tk.Toplevel(self.fenster)
        dialog.title("Workout eintragen")

        typ = tk.StringVar(value="kraft")
        tk.Radiobutton(dialog, text="Kraft", variable=typ, value="kraft").grid(row=0, column=0)
        tk.Radiobutton(dialog, text="Lauf", variable=typ, value="lauf").grid(row=0, column=1)

        felder = {}
        beschriftungen = [
            ("datum", "Datum (JJJJ-MM-TT)"),
            ("uebung", "Übung (nur Kraft)"),
            ("saetze", "Sätze (nur Kraft)"),
            ("wdh", "Wiederholungen (nur Kraft)"),
            ("gewicht", "Gewicht kg (nur Kraft)"),
            ("km", "Distanz km (nur Lauf)"),
            ("dauer_min", "Dauer min (nur Lauf)"),
        ]
        for zeile, (name, text) in enumerate(beschriftungen, start=1):
            tk.Label(dialog, text=text).grid(row=zeile, column=0, sticky="w", padx=8, pady=2)
            eingabe = tk.Entry(dialog)
            eingabe.grid(row=zeile, column=1, padx=8, pady=2)
            felder[name] = eingabe
        felder["datum"].insert(0, date.today().isoformat())

        def speichern():
            try:
                workout = self.workout_aus_formular(typ.get(), felder)
            except ValueError as fehler:
                messagebox.showerror("Ungültige Eingabe", str(fehler), parent=dialog)
                return
            workout_speichern(workout)
            dialog.destroy()
            self.kopf_aktualisieren()
            self.zeigen(print, "Workout gespeichert!")

        tk.Button(dialog, text="Speichern", command=speichern).grid(row=len(beschriftungen) + 1, column=0, columnspan=2, pady=8)

    @staticmethod
    def workout_aus_formular(typ, felder):
        """Liest das Formular aus und prüft die Eingaben. Wirft ValueError mit Hinweistext."""

        def zahl(name, text, ganzzahl=False, null_erlaubt=False):
            roh = felder[name].get().replace(",", ".")
            try:
                wert = int(roh) if ganzzahl else float(roh)
            except ValueError:
                raise ValueError(f"{text}: bitte eine gültige Zahl eingeben.")
            if wert < 0 or (wert == 0 and not null_erlaubt):
                raise ValueError(f"{text}: muss größer als 0 sein.")
            return wert

        workout = {spalte: "" for spalte in SPALTEN}
        try:
            workout["datum"] = datetime.strptime(felder["datum"].get().strip(), "%Y-%m-%d").date().isoformat()
        except ValueError:
            raise ValueError("Datum: Format JJJJ-MM-TT, z. B. 2026-10-15.")
        workout["typ"] = typ

        if typ == "kraft":
            workout["uebung"] = felder["uebung"].get().strip()
            if not workout["uebung"]:
                raise ValueError("Bitte eine Übung angeben.")
            workout["saetze"] = zahl("saetze", "Sätze", ganzzahl=True)
            workout["wdh"] = zahl("wdh", "Wiederholungen", ganzzahl=True)
            workout["gewicht"] = zahl("gewicht", "Gewicht", null_erlaubt=True)
        else:
            workout["uebung"] = "Lauf"
            workout["km"] = zahl("km", "Distanz")
            workout["dauer_min"] = zahl("dauer_min", "Dauer")
        return workout


if __name__ == "__main__":
    hauptfenster = tk.Tk()
    RealmOfRepsApp(hauptfenster)
    hauptfenster.mainloop()
