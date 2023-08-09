sudo apt update

sudo apt upgrade

sudo apt install python3-pyqt5 python3-pyqt5.qtwebengine

pip install configparser

git clone https://github.com/mluckau/adarts-browser.git --branch adarts-browser-pyqt5-raspberrypi --single-branch adarts-browser-qt5

cd adarts-browser-qt5

cp config_example.ini config.ini

nano config.ini (jetzt board_id durch die board ids ersetzen, beim ersten mal starten sollte style auf 0 gestellt werden damitmeine die passende ansicht auswählen kann, danach speichern)

python3 darts-browser.py

