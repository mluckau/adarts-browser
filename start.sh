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
# Die Log-Ausgabe erfolgt nun direkt durch das Python-Skript in den logs/ Ordner.
# Shell-Fehler (falls Python gar nicht startet) werden nach /tmp/adarts-browser.error.log geleitet.
./.venv/bin/python darts-browser.py 2> /tmp/adarts-browser.error.log
