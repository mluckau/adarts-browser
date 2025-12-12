# Installation

Diese Anleitung ist für Manjaro Xfce geschrieben, sollte aber, so oder so ähnlich, auch mit anderen Systemen funktionieren.

## X11vnc installieren

```bash
sudo pacman -S x11vnc
x11vnc -storepasswd 
```

(vnc Passwort anlegen)

### Service anlegen

``` bash
nano .local/share/systemd/user/x11vnc_user.service
```

``` bash
[Unit]
Description=Start x11vnc
After=default.target display-manager.service

[Service]
Type=simple
ExecStart=/usr/bin/x11vnc -ncache 0 -noxdamage --display :0 -rfbauth /home/{USER}/.vnc/passwd
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

### Service starten

``` bash
systemctl --user daemon-reload
systemctl enable --user x11vnc_user
systemctl start --user x11vnc_user
```

Als Client empfehle ich "Remmina"

## Autodartsbrowser Setup

**Für die Erstinstallation nutzen Sie bitte das `install.sh` Skript.**

Dieses Skript kümmert sich automatisch um die Erstellung der virtuellen Umgebung und die Installation aller notwendigen Abhängigkeiten.

1.  **Repository klonen:**
    ```bash
    git clone https://github.com/mluckau/adarts-browser.git
    cd adarts-browser
    ```
2.  **Installation starten:**
    ```bash
    ./install.sh
    ```
    Nach Abschluss des Skripts ist die Umgebung eingerichtet.

### Manuelle Einrichtung (nur bei Bedarf)
Falls Sie die Schritte manuell ausführen möchten:
``` bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Optional: cp config_example.ini config.ini (falls config_example.ini existiert und Sie eine Basis-Konfiguration wünschen)
```

### Konfiguration
Die `config.ini` wird beim ersten Start der Anwendung automatisch erstellt, falls sie noch nicht vorhanden ist. Sie können die Einstellungen bequem über das Web-Interface vornehmen oder die `config.ini` manuell bearbeiten (optional):

```bash
nano config.ini
```

Nach dem Start ist die Konfiguration bequem über den Browser unter `http://<IP-Adresse>:5000` erreichbar. Dort kann auch das Styling aktiviert werden.

## Adarts-Browser Autostart

### Startscript

Im Repository liegt bereits ein optimiertes Startskript namens `start.sh`. Dieses kümmert sich um eine kurze Wartezeit beim Booten, setzt die Display-Variable und schreibt Logs.

Stellen Sie sicher, dass es ausführbar ist:
```bash
chmod +x start.sh
```

(Optional) Falls Sie das Skript an einen anderen Ort verschieben, passen Sie ggf. die Pfade darin an. Die Standardversion ermittelt den Ort automatisch.

### Autostart Desktop Entry anlegen

``` bash
nano ~/.config/autostart/autodarts-browser.desktop
```

Passen Sie den Pfad bei `Exec` an Ihr Installationsverzeichnis an!

``` bash
[Desktop Entry]
Encoding=UTF-8
Version=0.9.4
Type=Application
Name=Autodarts-Browser
Comment=Der Autodarts-Browser
# Pfad ANPASSEN:
Exec=/home/michael/Coding/adarts-browser/start.sh
StartupNotify=false
Terminal=false
Hidden=false
```

### Fehlerbehebung

Startet die Anwendung nicht, prüfen Sie das Logfile:
```bash
cat logs/adarts-browser.log
```

## Mauszeiger ausblenden

```bash
sudo pacman -S unclutter
```

starten mit

``` bash
unclutter &
```
