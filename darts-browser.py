
#https://youtu.be/v02KG5S_ESo?t=549
import typing
import sys
from PyQt6 import QtCore
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtWidgets import QWidget
from PyQt6.QtWebEngineCore import *

class MyWebBrowser(QMainWindow):

    def __init__(self):
        
        self.window = QWidget()
        self.window.setWindowTitle("Autodarts Webbrowser")
        self.window.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        #self.window.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.layout = QVBoxLayout()
        self.horizontal = QHBoxLayout()

        self.browser1 = QWebEngineView()
        self.browser2 = QWebEngineView()

        #self.storage_location = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)

        self.profile1 = QWebEngineProfile("storage-1", self.browser1)
        self.profile2 = QWebEngineProfile("storage-2", self.browser2)


        self.webpage1 = QWebEnginePage(self.profile1, self.browser1)
        self.webpage2 = QWebEnginePage(self.profile2, self.browser2)

        self.browser1.setPage(self.webpage1)
        self.browser2.setPage(self.webpage2)

        self.layout.addWidget(self.browser1)
        self.layout.addWidget(self.browser2)

        self.browser1.load(QUrl("https://autodarts.io/boards/7350f3e4-21a0-4616-a37e-0e2ae0c16028/follow"))
        self.browser2.load(QUrl("https://autodarts.io/boards/7350f3e4-21a0-4616-a37e-0e2ae0c16028/follow"))

        self.window.setLayout(self.layout)
        self.window.showMaximized()

    
app = QApplication(sys.argv)
window = MyWebBrowser()
app.exec()



