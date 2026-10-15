# RoR Mobile

Handy-Version von Realm of Reps: eine HTML-Seite, ohne Installation und ohne Build-Tools.
Es gelten dieselben Regeln (XP, Level, Streak, Challenges) wie im Python-Programm. Die Wochen-Challenges sind dieselben wie am Mac.

| Datei | Zweck |
|---|---|
| `index.html` | die ganze App (HTML, CSS, JavaScript) |
| `sw.js` | Service Worker: speichert die App für die Nutzung ohne Internet |
| `icon.png` | Symbol am Home-Bildschirm |

**Daten:** Sie liegen nur am iPhone (localStorage), nicht im Internet. Unter **Daten → CSV exportieren** sicherst du sie als `training.csv`, im gleichen Format wie am Mac. Eine exportierte Datei kannst du am Mac als `training.csv` in den Projektordner legen und umgekehrt.

## Am iPhone öffnen

Die App braucht eine Adresse mit `https://`. Eine Datei direkt aus der Dateien-App startet am iPhone kein JavaScript. Gratis-Hosting geht über GitHub Pages.

### Variante A (empfohlen): eigenes öffentliches Repo nur für die App

GitHub Pages ist im Gratis-Konto nur für **öffentliche** Repos verfügbar. `Realm_of_Reps-RoR-` ist privat, darum kommt die App in ein zweites, öffentliches Repo. Darin liegen nur die 3 Dateien und keine Trainingsdaten.

1. github.com → **+** → **New repository** → Name `ror-mobile` → **Public** → **Create repository**
2. Auf der neuen Seite: **uploading an existing file** → `index.html`, `sw.js` und `icon.png` aus dem Ordner `mobile/` hineinziehen → **Commit changes**
3. Im Repo: **Settings → Pages** → Source **Deploy from a branch** → Branch **main**, Ordner **/ (root)** → **Save**
4. Nach ca. 1 Minute steht oben die Adresse, z. B. `https://djonas96.github.io/ror-mobile/`

**Update später:** geänderte Dateien in `ror-mobile` erneut hochladen (Schritt 2). Die App holt sich die neue Version beim nächsten Öffnen mit Internet.

### Variante B: direkt aus dem privaten Repo

- Dafür ist **GitHub Pro** nötig. Für Studierende ist es gratis über das GitHub Student Developer Pack (education.github.com).
- **Achtung:** Die Pages-Seite ist trotzdem öffentlich. Pages veröffentlicht nur das Hauptverzeichnis oder `/docs`. Damit wären auch `training.csv` und alle anderen Dateien öffentlich. Darum ist Variante A besser.

### Zum Home-Bildschirm hinzufügen

1. Adresse in **Safari** öffnen (nicht Chrome)
2. **Teilen-Symbol** (Quadrat mit Pfeil) → **Zum Home-Bildschirm** → **Hinzufügen**
3. Ab jetzt nur noch über das Symbol am Home-Bildschirm öffnen

Wichtig:
- Die App vom Home-Bildschirm hat **eigene Daten**, getrennt von Safari. Darum von Anfang an nur über das Symbol nutzen.
- Beim ersten Öffnen Internet haben, damit die App für offline gespeichert wird. Danach funktioniert alles außer dem Wetter auch ohne Internet.
- Ab und zu **Daten → CSV exportieren** als Sicherung, z. B. in die Dateien-App oder per AirDrop an den Mac.

## Am Mac ausprobieren

`index.html` per Doppelklick in Safari oder Chrome öffnen. Das funktioniert, nur der Offline-Modus ist dann aus.
