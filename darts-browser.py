import sys
import configparser
from PyQt6 import QtCore
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QHBoxLayout

# from PyQt6.QtGui import *
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QWidget
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage

config = configparser.ConfigParser()
config.read("config.ini")

url1 = config["url"]["url1"]
url2 = config["url"]["url2"]


class MyWebBrowser(QMainWindow):
    def __init__(self):
        self.window = QWidget()
        self.window.setWindowTitle("Autodarts Webbrowser")
        self.window.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        # self.window.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        # TODO Auswahl des Bildschirms implementieren
        """ self.screens = app.screens()
        print(self.screens)
        self.window.setScreen(self.screens[0]) """

        self.layout = QVBoxLayout()
        self.horizontal = QHBoxLayout()

        self.browser1 = QWebEngineView()
        self.browser2 = QWebEngineView()

        # self.storage_location = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)

        self.profile1 = QWebEngineProfile("storage-1", self.browser1)
        self.profile2 = QWebEngineProfile("storage-2", self.browser2)

        self.webpage1 = QWebEnginePage(self.profile1, self.browser1)
        self.webpage2 = QWebEnginePage(self.profile2, self.browser2)

        self.browser1.setPage(self.webpage1)
        self.browser2.setPage(self.webpage2)

        self.layout.addWidget(self.browser1)
        self.layout.addWidget(self.browser2)

        self.browser1.load(QUrl(url1))
        self.browser2.load(QUrl(url2))

        self.window.setLayout(self.layout)
        # self.window.showMaximized()
        self.window.showFullScreen()


app = QApplication(sys.argv)
window = MyWebBrowser()
app.exec()
