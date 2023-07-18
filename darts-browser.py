import sys
import os
import configparser
from PyQt6 import QtCore
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QWidget
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage

config = configparser.ConfigParser()
config.read("config.ini")

url1 = config["url"]["url1"]
url2 = config["url"]["url2"]


class MyWebBrowser(QMainWindow):
    def __init__(self):
        self.initUi()
        self.loadPages()
        # self.showWindow()

    def initUi(self):
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

        # Setup Browser 1
        self.browser1 = QWebEngineView()
        self.profile1 = QWebEngineProfile("storage-1", self.browser1)
        self.profile1.setPersistentStoragePath(os.getcwd() + ("/Storage1"))
        self.webpage1 = QWebEnginePage(self.profile1, self.browser1)
        self.browser1.setPage(self.webpage1)
        self.layout.addWidget(self.browser1)

        # Setup Browser 2
        self.browser2 = QWebEngineView()
        self.profile2 = QWebEngineProfile("storage-2", self.browser2)
        self.profile2.setPersistentStoragePath(os.getcwd() + ("/Storage2"))
        self.webpage2 = QWebEnginePage(self.profile2, self.browser2)
        self.browser2.setPage(self.webpage2)
        self.layout.addWidget(self.browser2)

        # set SignalHandler
        # TODO implement Signals um die geladenen Seiten mit Javascript zu manipulieren
        self.browser1.page().loadStarted.connect(self.onLoadFinished)
        self.browser1.urlChanged.connect(self.onLoadFinished)
        self.browser1.loadFinished.connect(self.onLoadFinished)

    def loadPages(self):
        self.browser1.setUrl(QUrl(url1))
        self.browser2.setUrl(QUrl(url2))

    def showWindow(self):
        self.window.setLayout(self.layout)
        self.window.showFullScreen()

    def onLoadFinished(self, ok):
        print("Hallo")


def main():
    app = QApplication(sys.argv)
    window = MyWebBrowser()
    window.showWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
