# Autodarts-Browser

Ein spezialisierter Kiosk-Browser zur Anzeige von [Autodarts](https://autodarts.io) "Follow"-Boards. Die Anwendung ist für den maus- und tastaturlosen Betrieb auf einem dedizierten Display (z.B. einem Fernseher über einem Dartboard) konzipiert und wird vollständig über eine Konfigurationsdatei gesteuert.

## Features

- **Anzeige von 1 oder 2 Boards**: Zeigt je nach Konfiguration ein oder zwei Autodarts-Boards übereinander an.
- **Vollbildmodus**: Startet automatisch im Vollbild auf einem festgelegten Bildschirm.
- **Zoom-Faktor**: Skalierung der Anzeige anpassbar (z.B. für große Fernseher).
- **Automatischer Login**: Kann sich automatisch in Autodarts einloggen, um private Boards anzuzeigen.
- **Auto-Refresh**: Lädt die Seiten in einem konfigurierbaren Intervall neu, um die Verbindung aktiv zu halten.
- **Offline-Erkennung**: Zeigt bei Verbindungsabbruch eine informative Warteseite anstatt eines Fehlers und verbindet sich automatisch neu.
- **QR-Code Connect**: Zeigt beim Start (und permanent im Setup-Modus) einen QR-Code auf dem Display an, um schnell zur Konfigurationsseite auf dem Smartphone zu gelangen.
- **In-App Updates**: Prüfen und Installieren von Updates direkt über das Web-Interface.
- **Benutzerdefiniertes Styling**: Injiziert eine benutzerdefinierte `style.css`-Datei, um das Aussehen der Autodarts-Seite anzupassen.
- **Theme-Verwaltung**: Speichere, lade, benenne um und lösche verschiedene CSS-Styles (Themes) über das Web-Interface.
- **Logo-Integration**: Blendet ein benutzerdefiniertes Logo über den Boards ein.
- **Fernwartung**: Änderungen an der `config.ini` werden zur Laufzeit erkannt und führen zu einem automatischen Neustart.
- **Web-Konfiguration**: Ermöglicht die einfache Verwaltung aller Einstellungen über eine Weboberfläche (Responsive Design für Smartphones).
- **Log-Viewer**: Anzeige der System-Logs direkt im Web-Interface zur einfachen Fehlersuche.
- **Headless-Betrieb**: Für Systeme ohne direkt angeschlossene Eingabegeräte konzipiert.

## Installation

### 1. Voraussetzungen
- Python 3.x muss installiert sein.
- Ein System mit grafischer Oberfläche (z.B. eine minimale Linux-Distribution mit einem X-Server).
- Git (für Updates).

### 2. Repository klonen
Öffnen Sie ein Terminal und klonen Sie das Repository:
```bash
git clone https://github.com/mluckau/adarts-browser.git
cd adarts-browser
```

### 3. Virtuelle Umgebung einrichten (Empfohlen)
Erstellen und aktivieren Sie eine virtuelle Umgebung, um Abhängigkeiten isoliert zu halten:
```bash
python -m venv .venv
source .venv/bin/activate
```
*(Hinweis: Unter Windows lautet der Aktivierungsbefehl `.\.venv\Scripts\activate`)*

### 4. Abhängigkeiten installieren
Installieren Sie die notwendigen Python-Pakete:
```bash
pip install -r requirements.txt
```

### 5. Konfiguration erstellen (Optional)
Wenn Sie die Konfiguration manuell über die `config.ini` vornehmen möchten, kopieren Sie die Beispielkonfiguration:
```bash
cp config_example.ini config.ini
```
Alternativ können Sie die Konfiguration auch bequem über das Web-Interface vornehmen, sobald die Anwendung gestartet ist.

## Anwendung starten

Um die Anwendung zu starten, führen Sie das Hauptskript aus, während Sie sich im Projektverzeichnis befinden und die virtuelle Umgebung aktiviert ist:
```bash
python darts-browser.py
```
Die Anwendung startet im Vollbildmodus auf dem konfigurierten Bildschirm. Um sie zu beenden, können Sie im Terminal `Strg+C` drücken.

## Web-Konfiguration

Nach dem Start der Anwendung ist eine komfortable Konfigurationsoberfläche über den Webbrowser erreichbar. Ein **QR-Code auf dem Display** erleichtert den ersten Zugriff.

1.  Scannen Sie den QR-Code auf dem Display oder öffnen Sie auf einem anderen Gerät einen Browser.
2.  Geben Sie die IP-Adresse des Geräts ein: `http://<IP-Adresse>:5000`

Über diese Oberfläche können Sie:
- Alle Einstellungen (inkl. Zoom-Faktor, QR-Code) bequem ändern und speichern.
- **Updates prüfen & installieren**: Mit einem Klick das System auf den neuesten Stand bringen.
- Das CSS für das Styling direkt im Browser bearbeiten (**Live-Update** auf dem TV-Bildschirm).
- **Themes verwalten**: Im CSS-Editor Themes speichern, laden oder löschen.
- Die Anwendung neu starten, den Browser-Cache löschen oder System-Logs einsehen.

## Manuelle Konfiguration (`config.ini`)

Alternativ zur Web-Oberfläche kann die Anwendung auch direkt über die `config.ini` gesteuert werden.

---

### `[main]`
Allgemeine Einstellungen für die Anwendung.

- **`device_name`**
  - Ein optionaler Name für das Gerät.
  - **Standard**: `""`

- **`browsers`**
  - Anzahl der Browser-Fenster (1 oder 2).
  - **Standard**: `1`

- **`show_qr`**
  - Zeigt beim Start einen QR-Code mit der Config-URL an.
  - **Werte**: `true` oder `false`
  - **Standard**: `true`

- **`qr_duration`**
  - Anzeigedauer des QR-Codes in Sekunden.
  - **Standard**: `15`

- **`refresh_interval_min`**
  - Intervall in Minuten für automatischen Reload.
  - **Standard**: `0`

- **`zoom_factor`**
  - Skaliert den Inhalt.
  - **Standard**: `1.0`

- **`screen`**
  - Index des Bildschirms.
  - **Standard**: `0`

---

### `[boards]`
Definiert die anzuzeigenden Autodarts-Boards.

- **`board1_id`**
  - Die UUID des ersten Boards.
- **`board2_id`**
  - Die UUID des zweiten Boards (nur bei `browsers = 2`).

---

### `[security]`
Einstellungen für die Sicherheit des Web-Interfaces.

- **`enable_auth`**
  - Aktiviert den Passwortschutz für das Web-Interface.
  - **Werte**: `true` oder `false`
  - **Standard**: `false`

- **`username`**
  - Der Benutzername für den Login.
  - **Standard**: `admin`

- **`password_hash`**
  - Der sicher gehashte Passwort-String.
  - *Hinweis: Bitte setzen Sie das Passwort über das Web-Interface. Das manuelle Eintragen von Klartext-Passwörtern hier funktioniert nicht.*

---

### `[style]`
Einstellungen für das benutzerdefinierte CSS-Styling.

- **`activate`**
  - Aktiviert das Injizieren der `style.css`-Datei.
  - **Standard**: `false`

---

### `[logos]`
Einstellungen für die Anzeige eines Logos.

- **`enable`**
  - Aktiviert die Logo-Anzeige.
  - **Standard**: `false`

- **`local`**
  - Wenn `true`, startet die Anwendung einen internen Webserver (auf einem zufälligen freien Port), um lokale Bilder bereitzustellen.
  - **Standard**: `false`

- **`logo`**
  - Die Quelle des Logos.
  - Wenn `local = true`: Der relative Pfad zur Bilddatei (z.B. `scripts/logo.png`).
  - Wenn `local = false`: Eine vollständige URL zu einem online gehosteten Bild.
  - **Standard**: `""`

- **`view_mode`**
  - Wählt automatisch einen Ansichtsmodus auf der Autodarts-Seite.
  - **Werte**: `none`, `Segments mode`, `Coords mode`, `Live mode`
  - **Standard**: `none`

---

### `[autologin]`
Einstellungen für den automatischen Login.

- **`enable`**
  - Aktiviert den automatischen Login.
  - **Standard**: `false`

- **`username`**
  - Autodarts Benutzername (E-Mail).

- **`password`** (früher `passwort`)
  - Autodarts Passwort.
  - *Hinweis:* Wenn das Passwort über das Web-Interface eingegeben wird, wird es verschlüsselt gespeichert. Sie können es auch als Klartext hier eintragen (nicht empfohlen), die Anwendung verschlüsselt es dann beim nächsten Zugriff über das Web-Interface automatisch.

- **`attempts`** (früher `versuche`)
  - Maximale Login-Versuche.
  - **Standard**: `3`

## Autostart (Beispiel für Linux)

Um die Anwendung automatisch beim Systemstart auszuführen, liegt dem Repository bereits ein optimiertes Startskript `start.sh` bei.

1.  **Start-Skript prüfen:**
    Die Datei `start.sh` im Hauptverzeichnis enthält bereits alle notwendigen Befehle (Wartezeit beim Boot, Display-Variable, Logging).
    Sie können diese Datei direkt verwenden oder an einen beliebigen Ort kopieren (dann müssen Sie ggf. den Pfad im Skript anpassen, falls die automatische Erkennung nicht greift).

    Stellen Sie sicher, dass sie ausführbar ist (sollte bereits der Fall sein):
    ```bash
    chmod +x start.sh
    ```

2.  **.desktop-Datei anlegen (in `~/.config/autostart/`):**
    Erstellen Sie eine Datei namens `autodarts-browser.desktop`:
    ```ini
    [Desktop Entry]
    Type=Application
    Name=Autodarts-Browser
    # Pfad bitte anpassen!
    Exec=/home/pi/adarts-browser/start.sh
    StartupNotify=false
    Terminal=false
    ```
    *Ersetzen Sie `/home/pi/adarts-browser/start.sh` durch den tatsächlichen absoluten Pfad zu Ihrer `start.sh`.*

**Tipp zur Fehlersuche:**
Das Skript schreibt Log-Ausgaben in den Unterordner `logs/`. Sollte die Anwendung nicht starten, prüfen Sie diese Datei:
```bash
cat logs/adarts-browser.log
```