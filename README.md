# Autodarts-Browser

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

Ein spezialisierter Kiosk-Browser zur Anzeige von [Autodarts](https://autodarts.io) "Follow"-Boards. Die Anwendung ist für den maus- und tastaturlosen Betrieb auf einem dedizierten Display (z.B. einem Fernseher über einem Dartboard) konzipiert und wird vollständig über eine Konfigurationsdatei gesteuert.

## Features

- **Anzeige von 1 oder 2 Boards**: Zeigt je nach Konfiguration ein oder zwei Autodarts-Boards übereinander an.
- **Vollbildmodus**: Startet automatisch im Vollbild auf einem festgelegten Bildschirm.
- **Zoom-Faktor**: Skalierung der Anzeige anpassbar (z.B. für große Fernseher).
- **Automatischer Login**: Kann sich automatisch in Autodarts einloggen.
- **Auto-Refresh**: Lädt die Seiten in einem konfigurierbaren Intervall neu, um die Verbindung aktiv zu halten.
- **Offline-Erkennung**: Zeigt bei Verbindungsabbruch eine informative Warteseite anstatt eines Fehlers und verbindet sich automatisch neu.
- **QR-Code Connect**: Zeigt beim Start (und permanent im Setup-Modus) einen QR-Code auf dem Display an, um schnell zur Konfigurationsseite auf dem Smartphone zu gelangen.
- **Automatischer Update-Check**: Prüft beim Start des Webinterfaces automatisch im Hintergrund auf Updates und zeigt einen Hinweis an.
- **In-App Updates**: Prüfen und Installieren von Updates direkt über das Web-Interface.
- **Benutzerdefiniertes Styling**: Injiziert eine benutzerdefinierte `style.css`-Datei, um das Aussehen der Autodarts-Seite anzupassen.
- **Online Theme Browser**: Durchsuchen und Installieren von Community-Themes direkt in der App (mit Vorschaubildern).
- **Theme-Verwaltung**: Speichere, lade, benenne um und lösche verschiedene CSS-Styles (Themes) über das Web-Interface.
- **Backup & Restore**: Sichern und Wiederherstellen der gesamten Konfiguration und Themes.
- **Logo-Integration**: Blendet ein benutzerdefiniertes Logo über den Boards ein.
- **Fernwartung**: Änderungen an der `config.ini` werden zur Laufzeit erkannt und führen zu einem automatischen Neustart.
- **Web-Konfiguration**: Ermöglicht die einfache Verwaltung aller Einstellungen über eine Weboberfläche (Responsive Design für Smartphones).
- **Log-Viewer**: Anzeige der System-Logs direkt im Web-Interface zur einfachen Fehlersuche.
- **Headless-Betrieb**: Für Systeme ohne direkt angeschlossene Eingabegeräte konzipiert.

## Community Themes

Der Autodarts-Browser verfügt über ein integriertes Online-Repository für Themes. Sie können vorgefertigte Designs direkt in der App installieren.

**Haben Sie ein tolles Theme erstellt?**
Wir freuen uns über Beiträge aus der Community! Sie haben zwei Möglichkeiten, Ihr Theme mit anderen zu teilen:

### 1. Per GitHub (Bevorzugt)
1. Exportieren Sie Ihr Theme im Web-Interface über den Button "📤 Exportieren". Füllen Sie dabei die Metadaten (Name, Autor, Beschreibung) aus.
2. Besuchen Sie das [Theme-Repository auf GitHub](https://github.com/mluckau/adarts-browser-themes).
3. Erstellen Sie einen **Fork** des Repositories.
4. Laden Sie Ihre `.css` Datei in den Ordner `themes/` hoch.
5. (Optional) Fügen Sie einen Screenshot Ihres Themes hinzu.
6. Bearbeiten Sie die `themes.json`, um Ihr Theme einzutragen (orientieren Sie sich an den vorhandenen Einträgen).
7. Erstellen Sie einen **Pull Request**.

### 2. Via GitHub Issues
1. Exportieren Sie Ihr Theme im Web-Interface über den Button "📤 Exportieren". Füllen Sie dabei die Metadaten (Name, Autor, Beschreibung) aus.
2. Besuchen Sie den **Issues-Bereich** des [Theme-Repository auf GitHub](https://github.com/mluckau/adarts-browser-themes/issues).
3. Erstellen Sie ein **neues Issue** und beschreiben Sie Ihr Theme.
4. Fügen Sie die exportierte `.css` Datei (und gerne auch einen Screenshot) als Anhang zum Issue hinzu.

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

### 3. Virtuelle Umgebung und Abhängigkeiten einrichten (Empfohlen)

**Einfache Installation mit dem Skript:**
Führen Sie das `install.sh` Skript aus, um die virtuelle Umgebung zu erstellen und alle Abhängigkeiten zu installieren:
```bash
./install.sh
```

Für eine manuelle Einrichtung, folgen Sie den Schritten in `install.md`.

### 4. Konfiguration erstellen (Optional)
Wenn Sie die Konfiguration manuell über die `config.ini` vornehmen möchten, kopieren Sie die Beispielkonfiguration:
```bash
cp config_example.ini config.ini
```
Alternativ können Sie die Konfiguration auch bequem über das Web-Interface vornehmen, sobald die Anwendung gestartet ist.

## Anwendung starten

Um die Anwendung zu starten, nutzen Sie das mitgelieferte Startskript:
```bash
./start.sh
```
Dieses Skript aktiviert automatisch die virtuelle Umgebung und startet die Anwendung im Vollbildmodus auf dem konfigurierten Bildschirm. Um sie zu beenden, können Sie im Terminal `Strg+C` drücken.

## Web-Konfiguration

Nach dem Start der Anwendung ist eine komfortable Konfigurationsoberfläche über den Webbrowser erreichbar. Ein **QR-Code auf dem Display** erleichtert den ersten Zugriff.

1.  Scannen Sie den QR-Code auf dem Display oder öffnen Sie auf einem anderen Gerät einen Browser.
2.  Geben Sie die IP-Adresse des Geräts ein: `http://<IP-Adresse>:5000`

Über diese Oberfläche können Sie:
- Alle Einstellungen (inkl. Zoom-Faktor, QR-Code) bequem ändern und speichern.
- **Automatischer Update-Check**: Das Webinterface prüft beim Start und in unregelmäßigen Abständen automatisch auf Updates.
- **Updates prüfen & installieren**: Wenn ein Update verfügbar ist (automatisch erkannt oder manuell geprüft), wechselt der "Updates suchen"-Button zu "Update installieren".
- Das CSS für das Styling direkt im Browser bearbeiten (**Live-Update** auf dem TV-Bildschirm).
- **Themes verwalten**: Im CSS-Editor Themes speichern, laden oder löschen.
- Die Anwendung neu starten, den Browser-Cache löschen oder System-Logs einsehen.

## Remote-Debugging (CSS-Elemente ermitteln)

Da der Kiosk-Rechner meist ohne Tastatur und Maus betrieben wird, ist das Ermitteln von CSS-Selektoren für das Custom Styling schwierig. Der Autodarts-Browser verfügt daher über eine integrierte Remote-Debugging-Funktion.

### Einrichtung & Nutzung:

1. **Aktivieren:** Öffnen Sie das Web-Interface, tragen Sie unter *Allgemeine Einstellungen* bei **Remote Debugging Port** einen freien Port ein (z.B. `9222`) und klicken Sie auf **Speichern & Neustarten** (Wert `0` deaktiviert die Funktion).
2. **PC verbinden:** Öffnen Sie an Ihrem PC oder Laptop (im selben Netzwerk) einen auf Chromium basierenden Browser (Google Chrome, Microsoft Edge, Brave etc.).
3. **Konfigurieren:** Rufen Sie im Browser die Spezialadresse `chrome://inspect` auf.
4. **IP eintragen:** Klicken Sie neben *Discover network targets* auf **Configure...** und fügen Sie die IP des Kiosk-PCs zusammen mit dem Port hinzu (z.B. `192.168.2.136:9222`). Bestätigen Sie mit **Done**.
5. **Inspizieren:** Unter *Remote Target* tauchen nach kurzer Zeit die offenen Tabs des Kiosk-Browsers auf. Klicken Sie auf **inspect**.
6. **CSS anpassen:** Es öffnet sich die gespiegelte Chrome-Entwicklerkonsole (F12). Sie können nun Elemente auswählen, CSS live testen und die fertigen Selektoren in den CSS-Editor des Web-Interfaces übertragen.

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

- **`remote_debugging_port`**
  - Port für remote Chromium Developer Tools.
  - **Werte**: `0` (deaktiviert) oder Portnummer (z.B. `9222`)
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

## Fehlerbehebung

### Grafische Probleme / Speicherzugriffsfehler (Segmentation Fault) in VMs

Wenn die Anwendung mit einem "Speicherzugriffsfehler" (Segmentation Fault) abstürzt, insbesondere in virtuellen Maschinen (VMs) oder auf Systemen ohne dedizierte Grafikkarte/3D-Beschleunigung (z.B. einige Raspberry Pi Setups), kann dies an der standardmäßigen Nutzung der Hardware-Beschleunigung durch die grafische Oberfläche liegen.

**Lösung:**
Fügen Sie die folgenden Zeilen am Anfang Ihrer `start.sh` (nach dem Shebang `#!/bin/bash` und vor `sleep 10`) hinzu, um die Hardware-Beschleunigung für Qt und die WebEngine zu deaktivieren und Software-Rendering zu erzwingen:

```bash
export QTWEBENGINE_CHROMIUM_FLAGS="--disable-gpu --disable-software-rasterizer"
export QT_XCB_GL_INTEGRATION=none
```
Dies zwingt die Anwendung, eine softwarebasierte Render-Methode zu verwenden, was solche Abstürze in Umgebungen mit eingeschränkter oder problematischer GPU-Unterstützung verhindern kann.

### Mauszeiger ausblenden (Optional)

Für einen reinen Anzeige-Modus (Kiosk) ist der Mauszeiger oft störend. Wir empfehlen das Tool `unclutter`.

*   **Installation:** Das `install.sh` Skript fragt Sie bei der Installation, ob `unclutter` installiert werden soll.
*   **Nutzung:** Damit der Mauszeiger verschwindet, muss `unclutter` im Hintergrund laufen. Fügen Sie dazu `unclutter &` in Ihre Autostart-Konfiguration (z.B. `.xinitrc` oder vor dem Startbefehl in der `.desktop` Datei) ein.

## Lizenz

Dieses Projekt ist unter der **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)** Lizenz veröffentlicht.

Kurzfassung:
*   ✅ **Teilen & Bearbeiten:** Sie dürfen den Code kopieren, verteilen und verändern.
*   👤 **Namensnennung:** Sie müssen den Urheber ([mluckau (GitHub)](https://github.com/mluckau)) nennen.
*   💲 **Nicht-kommerziell:** Sie dürfen das Projekt nicht für kommerzielle Zwecke nutzen.
*   🔄 **Weitergabe unter gleichen Bedingungen:** Wenn Sie den Code verändern, müssen Sie ihn unter derselben Lizenz veröffentlichen.

Den vollständigen Lizenztext finden Sie in der Datei `LICENSE`.