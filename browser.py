import sys
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import QApplication
app=QApplication(sys.argv)

w=QWebEngineView()
w.load(QUrl('https://google.com')) ## load google on startup
w.show()

sys.exit(app.exec_())