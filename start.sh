#!/bin/bash

# =============================================================================
# Autodarts-Browser Start Script
# =============================================================================

# 1. Wartezeit beim Systemstart
# Verhindert Fehler, wenn Netzwerk oder Grafik noch nicht bereit sind.
sleep 10

# 2. Display-Variable setzen
# Notwendig für GUI-Anwendungen, die aus dem Hintergrund gestartet werden.
export DISPLAY=:0

# 3. Verzeichnis bestimmen
# Ermittelt automatisch das Verzeichnis, in dem dieses Skript liegt.
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 4. In das Verzeichnis wechseln
cd "$SCRIPT_DIR" || { echo "Fehler: Konnte nicht nach $SCRIPT_DIR wechseln" > /tmp/adarts-browser.error.log; exit 1; }

# 5. Anwendung starten
# Nutzt den Python-Interpreter der virtuellen Umgebung (.venv).
# Schreibt Ausgaben (stdout) und Fehler (stderr) in eine Logdatei im logs/ Ordner.
mkdir -p logs
./.venv/bin/python darts-browser.py > logs/adarts-browser.log 2>&1
