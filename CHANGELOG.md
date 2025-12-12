# Changelog

Alle Änderungen am Projekt werden in dieser Datei dokumentiert.

## [0.3.1] - 2025-12-12

### Hinzugefügt
- **Theme-Verwaltung erweitert**:
  - Unterstützung für Theme-Autoren (Anzeige und Speicherung).
  - **Export-Funktion**: Themes können mit eingebetteten Metadaten (Name, Autor, Beschreibung, Version) exportiert werden.
  - **Import-Funktion**: Themes können per CSS-Datei importiert werden (optional mit Metadaten aus der Datei).
- **Vereinfachte Installation**:
  - Neues `install.sh` Skript für die automatische Ersteinrichtung der virtuellen Umgebung und Abhängigkeiten.
  - `install.sh` bietet nun optional die Installation von **Build-Tools** (z.B. `gcc`) und **`unclutter`** (zum Ausblenden des Mauszeigers) an, systemabhängig (`pacman`/`apt`).
- **Automatischer Update-Check**: Das Webinterface sucht nun automatisch im Hintergrund nach Updates.
- **Visueller Update-Indikator**: Ein grünes "Update verfügbar!"-Badge wird in der Navigationsleiste angezeigt, wenn ein Update entdeckt wird.
- **Automatischer Abhängigkeits-Check**: Nach einem In-App Update (`git pull`) werden nun automatisch neue Python-Abhängigkeiten (`pip install -r requirements.txt`) installiert.

### Geändert
- **Dokumentation**: `README.md` und `install.md` wurden aktualisiert, um den neuen Installationsprozess, die Theme-Beitragsmöglichkeiten (via GitHub Issues) und den Hinweis zur `unclutter`-Nutzung zu beschreiben.
- **UI/UX**: Metadaten-Kommentare (`/* VERSION: ... */`, `/* AUTHOR: ... */` etc.) werden beim Laden von CSS-Dateien in den Editor entfernt, um eine sauberere Bearbeitungsansicht zu ermöglichen.
- **Theme-Beitrag**: Option zur Einreichung von Themes nun auch über GitHub Issues.
- **`start.sh`**: VM-spezifische Grafikeinstellungen wurden entfernt, um das Skript generischer zu halten.
- **Update-Button-Logik**: Der "Updates suchen"-Button im Webinterface wechselt automatisch zu "Update installieren", wenn ein Update verfügbar ist.

### Behoben
- **Update-Abhängigkeitsinstallation**: Problem behoben, bei dem `pip` beim In-App Update nicht korrekt gefunden wurde (`pip` wird nun als `python -m pip` aufgerufen).
- **Theme-Metadaten-Duplikation**: Das Problem der doppelten Metadaten-Kommentare beim Speichern von Themes wurde behoben.
- **UX-Export-Modal**: Das Export-Modal schließt sich nun automatisch nach dem Initiieren eines Downloads.
- **Installation**: Behebung des Syntaxfehlers im `install.sh` Skript.

### Hinweise
- **Grafische Probleme in VMs**: Hinweise zur Behebung von "Speicherzugriffsfehlern" in virtuellen Umgebungen durch Deaktivierung der Hardware-Beschleunigung (`QTWEBENGINE_CHROMIUM_FLAGS`, `QT_XCB_GL_INTEGRATION`) wurden zur `README.md` hinzugefügt.

## [0.3.0] - 2025-12-12

### Hinzugefügt
- **Online Theme Browser**: Integrierter Store zum Durchsuchen, Installieren und Aktualisieren von Community-Themes (mit Vorschaubildern).
- **Backup & Restore**: Vollständige Sicherung und Wiederherstellung der Konfiguration und Themes als ZIP-Datei.
- **In-App Update**: System-Updates (Git Pull) können direkt über das Web-Interface geprüft und installiert werden.
- **QR-Code Connect**:
  - Automatisches Overlay beim Start (konfigurierbar) zeigt die IP-Adresse des Web-Interfaces.
  - Permanenter "Setup-Modus" mit QR-Code, wenn noch keine Board-ID konfiguriert ist.
- **Erweiterte Versionierung**: SemVer-basierte Versionsanzeige (z.B. `v0.3.0-5-g9a2b3c`) in Titelzeile und Web-Footer.
- **Web-Interface**:
  - **Responsive Design**: Optimierte Darstellung für Smartphones.
  - **Login-Komfort**: "Angemeldet bleiben"-Option (31 Tage).
  - **Feedback**: Erfolgs- und Fehlermeldungen blenden sich automatisch aus.
- **Dynamische Setup-Seite**: Zeigt die tatsächliche IP-Adresse des Geräts an, um die Einrichtung zu erleichtern.

### Geändert
- **Code-Basis**: Modularisierung (`utils.py`, `config_server.py`) und Nutzung von `netifaces`/`qrcode` für Netzwerkfunktionen.
- **Abhängigkeiten**: Aktualisiert auf neueste Versionen (PySide6 6.10.1, Flask 3.1.2).

## [0.2.0] - 2025-12-09

### Hinzugefügt
- **Ansichts-Modus**: Neue Option "Automatische Ansicht" (view_mode) unter "Styling & Logo", um zwischen "Segments mode", "Coords mode" und "Live mode" automatisch umzuschalten.
- **Autologin-Sicherheit**: Das Autodarts-Passwort wird nun lokal verschlüsselt (AES) in der `config.ini` gespeichert, wenn es über das Web-Interface gesetzt wird.
- **Logging**: Logs werden nun persistent im Ordner `logs/` (statt `/tmp`) gespeichert und sind somit auch nach einem Reboot verfügbar.
- **Code-Qualität**: Umfangreiches Refactoring und Zentralisierung der Konfigurationslogik.
- **Theme-Verwaltung**: Möglichkeit zum Umbenennen von gespeicherten Themes hinzugefügt.
- **Geräte-Identifikation**:
  - Automatische Generierung einer eindeutigen `device_id` beim ersten Start.
  - Option zum Festlegen eines `device_name` (z.B. "Keller"), der im Web-Interface angezeigt wird.
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
