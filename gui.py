"""
Grafisches Menü für Realm of Reps (Zusatz zu main.py).
Start mit:  python3 gui.py
Nutzt tkinter/ttk (bei Python dabei) und dieselben Funktionen wie das Konsolenmenü.
"""

import io
import tkinter as tk
from contextlib import redirect_stdout
from datetime import date, datetime
from tkinter import font, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from daten_kraft import (SPALTEN, workout_speichern, workouts_laden, letztes_workout_loeschen,
                         kalenderwoche, volumen_pro_woche)
from design import FARBEN, SCHRIFT
from lauf_gamification import (XP_PRO_LEVEL, xp_berechnen, level, streak, wochenkilometer,
                               challenges_der_woche, challenge_wert,
                               zeichne_pace, zeichne_wochenkilometer, zeichne_kraftvolumen)
from main import statistik_anzeigen
from wetter import ORT, REGEN_GRENZE, plan_laden, plan_zeile

# Schriften: (Name, Größe, Stil)
S_TITEL = (SCHRIFT, 20, "bold")
S_GROSS = (SCHRIFT, 26, "bold")
S_NORMAL = (SCHRIFT, 12)
S_KLEIN = (SCHRIFT, 10)
S_FETT = (SCHRIFT, 12, "bold")
S_MONO = "TkFixedFont"  # Schrift mit fester Breite des Systems (Spalten bleiben gerade)


def ausgabe_von(funktion, *argumente):
    """Führt eine Funktion aus, die mit print() arbeitet, und gibt den Text zurück."""
    puffer = io.StringIO()
    with redirect_stdout(puffer):
        funktion(*argumente)
    return puffer.getvalue().strip()


def fortschritt_text(challenge, wert):
    """Zeigt, wie weit eine Challenge ist, z. B. '3.2 / 5 km'."""
    typ, ziel = challenge["typ"], challenge["ziel"]
    if typ == "km":
        return f"{wert:.1f} / {ziel} km"
    if typ == "volumen":
        return f"{wert:.0f} / {ziel} kg"
    if typ in ("trainingstage", "streak"):
        return f"{wert} / {ziel} Tage"
    return "geschafft" if wert >= ziel else "noch nicht"


def stil_einrichten(fenster):
    """Farben und Schriften für alle ttk-Elemente festlegen.
    Das Theme 'clam' lässt eigene Farben zu (auch am Mac)."""
    font.nametofont("TkFixedFont").configure(size=12)
    stil = ttk.Style(fenster)
    stil.theme_use("clam")
    f = FARBEN
    stil.configure(".", background=f["hintergrund"], foreground=f["text"], font=S_NORMAL)
    stil.configure("Karte.TFrame", background=f["karte"])
    stil.configure("TNotebook", background=f["hintergrund"], borderwidth=1,
                   bordercolor=f["linie"], lightcolor=f["karte"], darkcolor=f["linie"])
    stil.configure("TNotebook.Tab", padding=(16, 8), background=f["hintergrund"],
                   foreground=f["text_leise"], bordercolor=f["linie"],
                   lightcolor=f["hintergrund"], darkcolor=f["linie"])
    stil.map("TNotebook.Tab", background=[("selected", f["karte"])],
             foreground=[("selected", f["akzent_dunkel"])])
    stil.configure("TButton", padding=(14, 8), background=f["akzent"], foreground="white",
                   borderwidth=0, focusthickness=0)
    stil.map("TButton", background=[("active", f["akzent_dunkel"]), ("pressed", f["akzent_dunkel"])])
    stil.configure("Leise.TButton", background=f["akzent_hell"], foreground=f["akzent_dunkel"])
    stil.map("Leise.TButton", background=[("active", f["linie"])])
    stil.configure("TRadiobutton", background=f["karte"])
    stil.map("TRadiobutton", background=[("active", f["karte"])])
    stil.configure("TEntry", fieldbackground=f["karte"], bordercolor=f["linie"],
                   lightcolor=f["linie"], darkcolor=f["linie"], padding=6)
    stil.configure("Gruen.Horizontal.TProgressbar", troughcolor=f["akzent_hell"],
                   background=f["akzent"], bordercolor=f["akzent_hell"],
                   lightcolor=f["akzent"], darkcolor=f["akzent"], thickness=10)


def kachel(eltern, titel):
    """Weiße Kachel mit dünnem Rahmen und kleiner Überschrift. Gibt den Innenbereich zurück."""
    rahmen = tk.Frame(eltern, bg=FARBEN["karte"], highlightthickness=1,
                      highlightbackground=FARBEN["linie"])
    tk.Label(rahmen, text=titel.upper(), font=S_KLEIN, bg=FARBEN["karte"],
             fg=FARBEN["text_leise"]).pack(anchor="w", padx=16, pady=(12, 0))
    innen = tk.Frame(rahmen, bg=FARBEN["karte"])
    innen.pack(fill="both", expand=True, padx=16, pady=(4, 14))
    return rahmen, innen


def label(eltern, text="", schrift=S_NORMAL, farbe=None, **optionen):
    """Kurzform für ein Label auf weißem Grund."""
    return tk.Label(eltern, text=text, font=schrift, bg=FARBEN["karte"],
                    fg=farbe or FARBEN["text"], **optionen)


class RealmOfRepsApp:
    def __init__(self, fenster):
        self.fenster = fenster
        fenster.title("Realm of Reps")
        fenster.geometry("920x720")
        fenster.minsize(760, 600)
        fenster.configure(bg=FARBEN["hintergrund"])
        stil_einrichten(fenster)

        self.kopfzeile_bauen()
        self.kacheln_bauen()

        self.tabs = ttk.Notebook(fenster)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.tab_workout()
        self.tab_statistik()
        self.tab_diagramme()
        self.tab_wetter()

        self.aktualisieren()

    # -----------------------------------------------------------
    # Oberer Bereich: Titel und Kacheln
    # -----------------------------------------------------------

    def kopfzeile_bauen(self):
        kopf = tk.Frame(self.fenster, bg=FARBEN["hintergrund"])
        kopf.pack(fill="x", padx=20, pady=(18, 10))
        tk.Label(kopf, text="Realm of Reps", font=S_TITEL, bg=FARBEN["hintergrund"],
                 fg=FARBEN["text"]).pack(side="left")
        heute = date.today()
        tk.Label(kopf, text=f"{heute:%d.%m.%Y}  ·  {kalenderwoche(heute.isoformat())}",
                 font=S_NORMAL, bg=FARBEN["hintergrund"],
                 fg=FARBEN["text_leise"]).pack(side="right")

    def kacheln_bauen(self):
        reihe = tk.Frame(self.fenster, bg=FARBEN["hintergrund"])
        reihe.pack(fill="x", padx=20, pady=(0, 16))
        for spalte, gewicht in enumerate((3, 2, 2, 5)):
            reihe.columnconfigure(spalte, weight=gewicht, uniform="kachel")

        # Level mit Fortschrittsbalken
        rahmen, innen = kachel(reihe, "Level")
        rahmen.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.level_label = label(innen, schrift=S_GROSS)
        self.level_label.pack(anchor="w")
        self.xp_balken = ttk.Progressbar(innen, style="Gruen.Horizontal.TProgressbar",
                                         maximum=XP_PRO_LEVEL)
        self.xp_balken.pack(fill="x", pady=(6, 4))
        self.xp_label = label(innen, schrift=S_KLEIN, farbe=FARBEN["text_leise"])
        self.xp_label.pack(anchor="w")

        # Streak
        rahmen, innen = kachel(reihe, "Streak")
        rahmen.grid(row=0, column=1, sticky="nsew", padx=(0, 10))
        self.streak_label = label(innen, schrift=S_GROSS)
        self.streak_label.pack(anchor="w")
        label(innen, "Tage in Folge", S_KLEIN, FARBEN["text_leise"]).pack(anchor="w")

        # Diese Woche
        rahmen, innen = kachel(reihe, "Diese Woche")
        rahmen.grid(row=0, column=2, sticky="nsew", padx=(0, 10))
        self.woche_km = label(innen, schrift=S_FETT)
        self.woche_km.pack(anchor="w", pady=(6, 2))
        self.woche_kg = label(innen, schrift=S_FETT)
        self.woche_kg.pack(anchor="w")

        # Challenges
        rahmen, self.challenge_bereich = kachel(reihe, "Challenges dieser Woche")
        rahmen.grid(row=0, column=3, sticky="nsew")

    def aktualisieren(self):
        """Liest die CSV neu ein und aktualisiert Kacheln, Statistik und Diagramm."""
        workouts = workouts_laden()
        xp = xp_berechnen(workouts)
        self.level_label.config(text=f"Level {level(xp)}")
        self.xp_balken.config(value=xp % XP_PRO_LEVEL)
        self.xp_label.config(text=f"{xp % XP_PRO_LEVEL} / {XP_PRO_LEVEL} XP  ·  {xp} gesamt")
        self.streak_label.config(text=str(streak(workouts)))

        kw = kalenderwoche(date.today().isoformat())
        self.woche_km.config(text=f"{wochenkilometer(workouts).get(kw, 0):.1f} km",
                             fg=FARBEN["akzent"])
        self.woche_kg.config(text=f"{volumen_pro_woche(workouts).get(kw, 0):.0f} kg",
                             fg=FARBEN["kraft"])

        for kind in self.challenge_bereich.winfo_children():
            kind.destroy()
        for challenge in challenges_der_woche(kw):
            wert = challenge_wert(challenge, workouts, kw)
            erledigt = wert >= challenge["ziel"]
            zeile = tk.Frame(self.challenge_bereich, bg=FARBEN["karte"])
            zeile.pack(fill="x", pady=(2, 4))
            zeile.columnconfigure(1, weight=1)
            label(zeile, "✔" if erledigt else "○", S_FETT,
                  FARBEN["akzent"] if erledigt else FARBEN["offen"]).grid(row=0, column=0, sticky="nw")
            label(zeile, challenge["text"], anchor="w").grid(row=0, column=1, sticky="w", padx=6)
            label(zeile, f"{fortschritt_text(challenge, wert)}  ·  +{challenge['xp']} XP",
                  S_KLEIN, FARBEN["text_leise"], anchor="w").grid(row=1, column=1, sticky="w", padx=6)

        self.letzte_eintraege_zeigen(workouts)
        self.statistik_zeigen(workouts)
        self.diagramm_zeigen(self.aktuelles_diagramm)

    # -----------------------------------------------------------
    # Tab: Workout eintragen
    # -----------------------------------------------------------

    def tab_workout(self):
        seite = ttk.Frame(self.tabs, style="Karte.TFrame", padding=20)
        self.tabs.add(seite, text="Workout eintragen")

        self.typ = tk.StringVar(value="kraft")
        auswahl = tk.Frame(seite, bg=FARBEN["karte"])
        auswahl.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))
        for text, wert in (("Kraft", "kraft"), ("Lauf", "lauf")):
            ttk.Radiobutton(auswahl, text=text, variable=self.typ, value=wert,
                            command=self.felder_umschalten).pack(side="left", padx=(0, 16))

        self.felder = {}
        self.feld_zeilen = {}
        beschriftungen = [
            ("datum", "Datum (JJJJ-MM-TT)"),
            ("uebung", "Übung"),
            ("saetze", "Sätze"),
            ("wdh", "Wiederholungen pro Satz"),
            ("gewicht", "Gewicht in kg (0 = Körpergewicht)"),
            ("km", "Distanz in km"),
            ("dauer_min", "Dauer in Minuten"),
        ]
        for zeile, (name, text) in enumerate(beschriftungen, start=1):
            beschriftung = label(seite, text, farbe=FARBEN["text_leise"])
            beschriftung.grid(row=zeile, column=0, sticky="w", pady=4, padx=(0, 16))
            eingabe = ttk.Entry(seite, width=24)
            eingabe.grid(row=zeile, column=1, sticky="w", pady=4)
            self.felder[name] = eingabe
            self.feld_zeilen[name] = (beschriftung, eingabe)
        self.felder["datum"].insert(0, date.today().isoformat())

        knoepfe = tk.Frame(seite, bg=FARBEN["karte"])
        knoepfe.grid(row=9, column=0, columnspan=2, sticky="w", pady=(16, 0))
        ttk.Button(knoepfe, text="Speichern", command=self.speichern).pack(side="left")
        ttk.Button(knoepfe, text="Letzten Eintrag löschen", style="Leise.TButton",
                   command=self.letzten_loeschen).pack(side="left", padx=10)
        self.meldung = label(seite, farbe=FARBEN["akzent"])
        self.meldung.grid(row=10, column=0, columnspan=2, sticky="w", pady=(10, 0))

        # Rechts: die letzten Einträge
        seite.columnconfigure(2, weight=1)
        label(seite, "LETZTE EINTRÄGE", S_KLEIN, FARBEN["text_leise"]).grid(
            row=0, column=2, sticky="nw", padx=(40, 0))
        self.letzte_liste = label(seite, schrift=S_MONO, justify="left", anchor="nw")
        self.letzte_liste.grid(row=1, column=2, rowspan=9, sticky="nw", padx=(40, 0))

        self.felder_umschalten()

    def felder_umschalten(self):
        """Zeigt nur die Felder, die zum gewählten Typ passen."""
        kraft_felder = ("uebung", "saetze", "wdh", "gewicht")
        lauf_felder = ("km", "dauer_min")
        sichtbar = kraft_felder if self.typ.get() == "kraft" else lauf_felder
        for name in kraft_felder + lauf_felder:
            for element in self.feld_zeilen[name]:
                if name in sichtbar:
                    element.grid()
                else:
                    element.grid_remove()

    def letzte_eintraege_zeigen(self, workouts):
        zeilen = []
        for w in workouts[-8:][::-1]:
            if w["typ"] == "lauf":
                details = f"{float(w['km']):g} km in {float(w['dauer_min']):g} min"
            else:
                details = f"{w['uebung']} {w['saetze']}×{w['wdh']}"
                if float(w["gewicht"]) > 0:
                    details += f" @ {float(w['gewicht']):g} kg"
            zeilen.append(f"{w['datum'][8:]}.{w['datum'][5:7]}.  {details}")
        self.letzte_liste.config(text="\n".join(zeilen) or "Noch keine Einträge.")

    def speichern(self):
        try:
            workout = self.workout_aus_formular(self.typ.get(), self.felder)
        except ValueError as fehler:
            messagebox.showerror("Ungültige Eingabe", str(fehler), parent=self.fenster)
            return
        workout_speichern(workout)
        for name, eingabe in self.felder.items():
            if name not in ("datum", "uebung"):
                eingabe.delete(0, tk.END)
        self.meldung.config(text="✔ Workout gespeichert!")
        self.aktualisieren()

    def letzten_loeschen(self):
        if not messagebox.askyesno("Löschen", "Letzten Eintrag wirklich löschen?",
                                   parent=self.fenster):
            return
        geloescht = letztes_workout_loeschen()
        if geloescht is None:
            self.meldung.config(text="Es gibt noch keine Einträge.")
        else:
            self.meldung.config(text=f"Gelöscht: {geloescht['datum']} {geloescht['uebung']}")
        self.aktualisieren()

    @staticmethod
    def workout_aus_formular(typ, felder):
        """Liest das Formular aus und prüft die Eingaben. Wirft ValueError mit Hinweistext."""

        def zahl(name, text, ganzzahl=False, null_erlaubt=False):
            roh = felder[name].get().strip().replace(",", ".")
            try:
                wert = int(roh) if ganzzahl else float(roh)
            except ValueError:
                raise ValueError(f"{text}: bitte eine gültige Zahl eingeben.")
            if wert < 0 or (wert == 0 and not null_erlaubt):
                raise ValueError(f"{text}: muss größer als 0 sein.")
            return wert

        workout = {spalte: "" for spalte in SPALTEN}
        try:
            datum = datetime.strptime(felder["datum"].get().strip(), "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Datum: Format JJJJ-MM-TT, z. B. 2026-10-15.")
        if datum > date.today():
            raise ValueError("Datum: liegt in der Zukunft.")
        workout["datum"] = datum.isoformat()
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

    # -----------------------------------------------------------
    # Tab: Statistik
    # -----------------------------------------------------------

    def tab_statistik(self):
        seite = ttk.Frame(self.tabs, style="Karte.TFrame", padding=20)
        self.tabs.add(seite, text="Statistik")
        self.statistik_text = tk.Text(seite, font=S_MONO, bg=FARBEN["karte"], fg=FARBEN["text"],
                                      relief="flat", highlightthickness=0, wrap="none")
        self.statistik_text.pack(fill="both", expand=True)

    def statistik_zeigen(self, workouts):
        self.statistik_text.config(state="normal")
        self.statistik_text.delete("1.0", tk.END)
        self.statistik_text.insert(tk.END, ausgabe_von(statistik_anzeigen, workouts))
        self.statistik_text.config(state="disabled")  # nur lesen

    # -----------------------------------------------------------
    # Tab: Diagramme (im Fenster eingebettet)
    # -----------------------------------------------------------

    def tab_diagramme(self):
        seite = ttk.Frame(self.tabs, style="Karte.TFrame", padding=16)
        self.tabs.add(seite, text="Diagramme")
        self.diagramme = {
            "Pace": (zeichne_pace, "Noch keine Läufe eingetragen."),
            "Wochen-km": (zeichne_wochenkilometer, "Noch keine Läufe eingetragen."),
            "Kraftvolumen": (zeichne_kraftvolumen, "Noch keine Krafteinheiten eingetragen."),
        }
        self.aktuelles_diagramm = "Pace"

        leiste = tk.Frame(seite, bg=FARBEN["karte"])
        leiste.pack(fill="x")
        for name in self.diagramme:
            ttk.Button(leiste, text=name, style="Leise.TButton",
                       command=lambda n=name: self.diagramm_zeigen(n)).pack(side="left", padx=(0, 8))

        self.figur = Figure(figsize=(7, 3.6), dpi=100)
        self.leinwand = FigureCanvasTkAgg(self.figur, master=seite)
        self.leinwand.get_tk_widget().pack(fill="both", expand=True, pady=(12, 0))

    def diagramm_zeigen(self, name):
        self.aktuelles_diagramm = name
        zeichnen, meldung = self.diagramme[name]
        self.figur.clear()
        ax = self.figur.add_subplot()
        if not zeichnen(ax, workouts_laden()):
            ax.axis("off")
            ax.text(0.5, 0.5, meldung, ha="center", va="center", color=FARBEN["text_leise"])
            self.figur.set_facecolor(FARBEN["karte"])
        self.figur.tight_layout()
        self.leinwand.draw()

    # -----------------------------------------------------------
    # Tab: Wetter-Trainingsplan
    # -----------------------------------------------------------

    def tab_wetter(self):
        seite = ttk.Frame(self.tabs, style="Karte.TFrame", padding=20)
        self.tabs.add(seite, text="Wetter-Plan")
        label(seite, f"Trainingsplan {ORT}: Lauf nur bis {REGEN_GRENZE} % Regen, sonst Kraft.",
              farbe=FARBEN["text_leise"]).pack(anchor="w")
        ttk.Button(seite, text="Wetter laden", command=self.wetter_laden).pack(anchor="w", pady=12)
        self.wetter_bereich = tk.Frame(seite, bg=FARBEN["karte"])
        self.wetter_bereich.pack(fill="both", expand=True)

    def wetter_laden(self):
        for kind in self.wetter_bereich.winfo_children():
            kind.destroy()
        self.fenster.config(cursor="watch")
        self.fenster.update()
        plan = plan_laden()
        self.fenster.config(cursor="")
        if plan is None:
            label(self.wetter_bereich, "Wetterdaten konnten nicht geladen werden (Internet?).",
                  farbe=FARBEN["offen"]).pack(anchor="w")
            return
        for datum, prozent, einheit in plan:
            zeile = tk.Frame(self.wetter_bereich, bg=FARBEN["karte"])
            zeile.pack(fill="x", pady=3)
            text = plan_zeile(datum, prozent, einheit).split("→")[0]
            label(zeile, text, S_MONO).pack(side="left")
            farbe = FARBEN["akzent"] if einheit == "Lauf" else FARBEN["kraft"]
            tk.Label(zeile, text=f"  {einheit}  ", font=S_FETT, bg=farbe,
                     fg="white").pack(side="left", padx=8)


if __name__ == "__main__":
    hauptfenster = tk.Tk()
    RealmOfRepsApp(hauptfenster)
    hauptfenster.mainloop()
