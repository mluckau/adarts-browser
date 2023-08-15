## X11vnc installieren

### x11vnc installieren

sudo pacman -S x11vnc

x11vnc -storepasswd (vnc Passwort anlegen)

## Service anlegen

nano .local/share/systemd/user/x11vnc_user.service

______;
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

________;

## Service starten

systemctl --user daemon-reload
systemctl enable --user x11vnc_user
systemctl start --user x11vnc_user

## Autodartsbrowser Setup

Repository clonen

cd adarts-browser

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

cp config_example.ini config.ini

config.ini bearbeiten(style activate = o)

python darts-browser.py (alles einstellen)

config.ini bearbeiten(style activate = 1)

## Adarts Autostart

### Startscript anlegen

mkdir scripts
nano ~/scripts/start_dartsbrowser.sh
____;
!#/bin/bash
cd ~/adarts-browser/
source .venv/bin/activate
python darts-browser.py
____;
chmod +x start_dartsbrowser.sh

### Desktop Entry anlegen

nano ~/.config/autostart/autodarts-browser.desktop

[Desktop Entry]
Encoding=UTF-8
Version=0.9.4
Type=Application
Name=Autodarts-Browser
Comment=Der autodarts-Browser
Exec=/home/[USER]/scripts/start_dartsbrowser.sh
StartupNotify=false
Terminal=false
Hidden=false

