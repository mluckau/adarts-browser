# Changelog

Alle Änderungen am Projekt werden in dieser Datei dokumentiert.

## [Unreleased] - 2025-12-08

### Hinzugefügt
- **Konfiguration**: Vereinheitlichung der Konfigurationsschlüssel für Autologin von Deutsch auf Englisch (`passwort` -> `password`, `versuche` -> `attempts`) mit Abwärtskompatibilität.
- **Dynamischer HTTP-Server Port**: Der lokale HTTP-Server (für Logos) wählt nun automatisch einen freien Port, statt einen festen Port zu verwenden.
- **Sicherheit**:
  - Optionaler Passwortschutz für das Web-Interface.
  - Passwörter werden sicher gehasht in der `config.ini` gespeichert.
  - Login/Logout-Funktionalität.
- **Web-Interface zur Konfiguration**:
  - Vollständige Konfiguration über Browser (`http://<IP>:5000`)
  - Live-Bearbeitung von `style.css` mit sofortiger Aktualisierung auf dem Display
  - Theme-Manager zum Speichern, Laden und Löschen von CSS-Themes
  - Log-Viewer zur Anzeige von Systemprotokollen
  - Buttons zum Neustarten der App und Neuladen der Webseiten
- **Zoom-Faktor**: Neue Einstellung `zoom_factor` in `config.ini` und Web-Interface zur Skalierung der Anzeige.
- **Offline-Erkennung**:
  - Automatisches Overlay bei Verbindungsverlust
  - Automatischer Reconnect-Versuch
  - Eigene Fehlerseite (`templates/offline_page.html`) statt Standard-Browser-Fehler
- **Verbesserter Autostart**:
  - Neues `start.sh` Skript mit Logging nach `/tmp/adarts-browser.log`
  - Robusterer Startprozess mit `sleep` und `DISPLAY`-Variable
- **Backend-Verbesserungen**:
  - Umstellung auf `QFileSystemWatcher` für zuverlässigere Config-Updates
  - Base64-Encoding für CSS- und Script-Injection zur Vermeidung von Syntaxfehlern
  - Zentraler Handler für Dateiänderungen (Config, CSS, Trigger)

### Geändert
- **Projektstruktur**:
  - Templates in `templates/` Ordner verschoben und modularisiert (`base.html`)
  - Skripte in `scripts/` Ordner organisiert
  - Konfiguration von `config_server.py` und `darts-browser.py` harmonisiert
- **Dokumentation**:
  - `README.md` komplett überarbeitet mit allen neuen Features
  - `install.md` aktualisiert und vereinfacht

### Behoben
- Fehlerhafte Syntax in injizierten JavaScripts durch Base64-Encoding behoben
- Problem mit mehrfachen Restarts durch fehlerhafte Watcher-Logik behoben
- Crash-Handling verbessert: Fehler werden nun in `crash.log` geschrieben
